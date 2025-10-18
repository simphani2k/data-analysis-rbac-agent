#!/usr/bin/env python3
"""
Security Group Checker for RDS SSH Tunnel Setup

This script checks and optionally fixes security group configurations
needed for SSH tunneling to RDS.

Usage:
    python scripts/check_security_groups.py check    # Check current config
    python scripts/check_security_groups.py fix      # Fix security groups
"""

import os
import sys
import requests
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment
load_dotenv()


class SecurityGroupChecker:
    """Check and fix security group configurations."""

    def __init__(self):
        """Initialize with AWS configuration."""
        self.region = os.getenv('AWS_REGION', 'us-east-2')
        self.ec2_ip = os.getenv('SSH_HOST')
        self.rds_endpoint = os.getenv('RDS_HOST')

        try:
            self.ec2_client = boto3.client('ec2', region_name=self.region)
            self.rds_client = boto3.client('rds', region_name=self.region)
        except Exception as e:
            print(f"❌ Failed to initialize AWS clients: {e}")
            print("   Please configure AWS credentials:")
            print("   - Run: aws configure")
            print("   - Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env")
            sys.exit(1)

    def get_my_ip(self) -> str:
        """Get current public IP address."""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️  Could not determine public IP: {e}")
            return None

    def find_ec2_instance(self):
        """Find EC2 instance by public IP."""
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'ip-address', 'Values': [self.ec2_ip]}
                ]
            )

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    return instance

            return None
        except ClientError as e:
            print(f"❌ Error finding EC2 instance: {e}")
            return None

    def find_rds_instance(self):
        """Find RDS instance by endpoint."""
        try:
            # Extract DB instance identifier from endpoint
            db_identifier = self.rds_endpoint.split('.')[0]

            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=db_identifier
            )

            if response['DBInstances']:
                return response['DBInstances'][0]

            return None
        except ClientError as e:
            print(f"❌ Error finding RDS instance: {e}")
            return None

    def check_ec2_security_group(self, instance, my_ip):
        """Check if EC2 security group allows SSH from my IP."""
        print("\n" + "=" * 60)
        print("EC2 SECURITY GROUP CHECK")
        print("=" * 60)

        security_groups = instance['SecurityGroups']
        print(f"Instance: {instance['InstanceId']}")
        print(f"Security Groups: {len(security_groups)}")

        ssh_allowed = False

        for sg in security_groups:
            sg_id = sg['GroupId']
            sg_name = sg['GroupName']
            print(f"\n🔍 Checking {sg_name} ({sg_id})")

            # Get security group details
            sg_details = self.ec2_client.describe_security_groups(
                GroupIds=[sg_id]
            )['SecurityGroups'][0]

            # Check inbound rules
            for rule in sg_details['IpPermissions']:
                if rule.get('FromPort') == 22 and rule.get('ToPort') == 22:
                    print(f"   Found SSH rule (port 22):")

                    # Check IP ranges
                    for ip_range in rule.get('IpRanges', []):
                        cidr = ip_range['CidrIp']
                        print(f"      - Allows from: {cidr}")

                        if cidr == '0.0.0.0/0' or cidr == f'{my_ip}/32':
                            ssh_allowed = True
                            print(f"         ✅ Your IP is allowed!")

        if ssh_allowed:
            print(f"\n✅ SSH access is properly configured")
        else:
            print(f"\n❌ SSH access is NOT configured for your IP")
            print(f"   Your IP: {my_ip}")
            print(f"   Required: Add inbound rule for SSH (port 22) from {my_ip}/32")

        return ssh_allowed, security_groups[0]['GroupId'] if security_groups else None

    def check_rds_security_group(self, db_instance, ec2_sg_id):
        """Check if RDS security group allows access from EC2."""
        print("\n" + "=" * 60)
        print("RDS SECURITY GROUP CHECK")
        print("=" * 60)

        vpc_security_groups = db_instance['VpcSecurityGroups']
        print(f"RDS Instance: {db_instance['DBInstanceIdentifier']}")
        print(f"Security Groups: {len(vpc_security_groups)}")

        rds_allowed = False

        for sg in vpc_security_groups:
            sg_id = sg['VpcSecurityGroupId']
            print(f"\n🔍 Checking {sg_id}")

            # Get security group details
            sg_details = self.ec2_client.describe_security_groups(
                GroupIds=[sg_id]
            )['SecurityGroups'][0]

            # Check inbound rules
            for rule in sg_details['IpPermissions']:
                if rule.get('FromPort') == 5432 and rule.get('ToPort') == 5432:
                    print(f"   Found PostgreSQL rule (port 5432):")

                    # Check source security groups
                    for user_id_group_pair in rule.get('UserIdGroupPairs', []):
                        source_sg = user_id_group_pair['GroupId']
                        print(f"      - Allows from SG: {source_sg}")

                        if source_sg == ec2_sg_id:
                            rds_allowed = True
                            print(f"         ✅ EC2 security group is allowed!")

                    # Check IP ranges
                    for ip_range in rule.get('IpRanges', []):
                        cidr = ip_range['CidrIp']
                        print(f"      - Allows from CIDR: {cidr}")

        if rds_allowed:
            print(f"\n✅ RDS access from EC2 is properly configured")
        else:
            print(f"\n❌ RDS access from EC2 is NOT configured")
            print(f"   EC2 SG: {ec2_sg_id}")
            print(f"   Required: Add inbound rule for PostgreSQL (port 5432) from EC2 SG")

        return rds_allowed, vpc_security_groups[0]['VpcSecurityGroupId'] if vpc_security_groups else None

    def fix_ec2_security_group(self, sg_id, my_ip):
        """Add SSH rule to EC2 security group."""
        print(f"\n🔧 Adding SSH rule to {sg_id}...")

        try:
            self.ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [
                            {
                                'CidrIp': f'{my_ip}/32',
                                'Description': 'SSH from my local machine'
                            }
                        ]
                    }
                ]
            )
            print(f"✅ SSH rule added successfully!")
            return True

        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
                print(f"⚠️  Rule already exists")
                return True
            else:
                print(f"❌ Failed to add rule: {e}")
                return False

    def fix_rds_security_group(self, rds_sg_id, ec2_sg_id):
        """Add PostgreSQL rule to RDS security group."""
        print(f"\n🔧 Adding PostgreSQL rule to {rds_sg_id}...")

        try:
            self.ec2_client.authorize_security_group_ingress(
                GroupId=rds_sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 5432,
                        'ToPort': 5432,
                        'UserIdGroupPairs': [
                            {
                                'GroupId': ec2_sg_id,
                                'Description': 'PostgreSQL from EC2 bastion'
                            }
                        ]
                    }
                ]
            )
            print(f"✅ PostgreSQL rule added successfully!")
            return True

        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
                print(f"⚠️  Rule already exists")
                return True
            else:
                print(f"❌ Failed to add rule: {e}")
                return False

    def check_all(self):
        """Check all security group configurations."""
        print("=" * 60)
        print("SECURITY GROUP CONFIGURATION CHECKER")
        print("=" * 60)

        # Get my IP
        my_ip = self.get_my_ip()
        if not my_ip:
            print("❌ Could not determine public IP")
            return False

        print(f"Your public IP: {my_ip}")
        print(f"EC2 Instance: {self.ec2_ip}")
        print(f"RDS Endpoint: {self.rds_endpoint}")

        # Find EC2 instance
        ec2_instance = self.find_ec2_instance()
        if not ec2_instance:
            print("❌ Could not find EC2 instance")
            return False

        # Check EC2 security group
        ec2_ok, ec2_sg_id = self.check_ec2_security_group(ec2_instance, my_ip)

        # Find RDS instance
        rds_instance = self.find_rds_instance()
        if not rds_instance:
            print("⚠️  Could not find RDS instance")
            print("   Manual verification required")
            return ec2_ok

        # Check RDS security group
        rds_ok, rds_sg_id = self.check_rds_security_group(rds_instance, ec2_sg_id)

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        if ec2_ok and rds_ok:
            print("✅ All security groups properly configured!")
            print("\nYou can now run:")
            print("   python scripts/ssh_tunnel_manager.py start")
        else:
            print("❌ Security groups need configuration")
            if not ec2_ok:
                print(f"   - EC2: Add SSH rule for {my_ip}/32")
            if not rds_ok:
                print(f"   - RDS: Add PostgreSQL rule for EC2 SG {ec2_sg_id}")
            print("\nRun with 'fix' to automatically configure:")
            print("   python scripts/check_security_groups.py fix")

        return ec2_ok and rds_ok

    def fix_all(self):
        """Fix all security group configurations."""
        print("=" * 60)
        print("SECURITY GROUP AUTO-FIX")
        print("=" * 60)

        # Get my IP
        my_ip = self.get_my_ip()
        if not my_ip:
            print("❌ Could not determine public IP")
            return False

        print(f"Your public IP: {my_ip}")

        # Find EC2 instance
        ec2_instance = self.find_ec2_instance()
        if not ec2_instance:
            print("❌ Could not find EC2 instance")
            return False

        ec2_sg_id = ec2_instance['SecurityGroups'][0]['GroupId']

        # Fix EC2 security group
        self.fix_ec2_security_group(ec2_sg_id, my_ip)

        # Find RDS instance
        rds_instance = self.find_rds_instance()
        if rds_instance:
            rds_sg_id = rds_instance['VpcSecurityGroups'][0]['VpcSecurityGroupId']
            # Fix RDS security group
            self.fix_rds_security_group(rds_sg_id, ec2_sg_id)

        print("\n✅ Security groups updated!")
        print("\nTest SSH connection:")
        print(f"   ssh -i ~/.ssh/dev01.pem ec2-user@{self.ec2_ip}")

        return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_security_groups.py {check|fix}")
        print("\nCommands:")
        print("  check - Check current security group configuration")
        print("  fix   - Automatically fix security group issues")
        sys.exit(1)

    command = sys.argv[1].lower()

    if not os.path.exists('.env'):
        print("⚠️  No .env file found!")
        sys.exit(1)

    checker = SecurityGroupChecker()

    if command == 'check':
        success = checker.check_all()
        sys.exit(0 if success else 1)

    elif command == 'fix':
        success = checker.fix_all()
        sys.exit(0 if success else 1)

    else:
        print(f"❌ Unknown command: {command}")
        print("Valid commands: check, fix")
        sys.exit(1)


if __name__ == "__main__":
    main()
