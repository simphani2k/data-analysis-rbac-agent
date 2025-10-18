#!/usr/bin/env python3
"""
SSH Tunnel Manager for Secure RDS Access

This script manages SSH tunneling to AWS RDS instances through a bastion/EC2 host.
It provides a secure way to connect to private RDS instances without exposing them publicly.

Usage:
    # Start tunnel
    python scripts/ssh_tunnel_manager.py start

    # Check tunnel status
    python scripts/ssh_tunnel_manager.py status

    # Stop tunnel
    python scripts/ssh_tunnel_manager.py stop

    # Test connection through tunnel
    python scripts/ssh_tunnel_manager.py test

Prerequisites:
    - EC2 instance in same VPC as RDS (bastion host)
    - SSH key file (.pem) for EC2 access
    - Security group allowing EC2 → RDS on port 5432
    - .env file with SSH configuration
"""

import os
import sys
import subprocess
import time
import signal
from typing import Optional
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()


class SSHTunnelManager:
    """Manage SSH tunnel for secure RDS access."""

    def __init__(self):
        """Initialize tunnel manager with configuration from environment."""
        # RDS configuration
        self.rds_host = os.getenv('RDS_HOST')
        self.rds_port = os.getenv('RDS_PORT', '5432')
        self.rds_database = os.getenv('RDS_DATABASE')
        self.rds_user = os.getenv('RDS_USER')
        self.rds_password = os.getenv('RDS_PASSWORD')

        # SSH tunnel configuration
        self.ssh_host = os.getenv('SSH_HOST')
        self.ssh_user = os.getenv('SSH_USER', 'ec2-user')
        self.ssh_key_path = os.path.expanduser(os.getenv('SSH_KEY_PATH', '~/.ssh/id_rsa'))
        self.local_port = os.getenv('SSH_LOCAL_PORT', '5433')

        # Tunnel process tracking
        self.pid_file = '.ssh_tunnel.pid'

    def validate_config(self) -> bool:
        """Validate SSH tunnel configuration."""
        print("=" * 60)
        print("SSH TUNNEL CONFIGURATION")
        print("=" * 60)

        config_valid = True

        # Check RDS config
        if not all([self.rds_host, self.rds_database, self.rds_user, self.rds_password]):
            print("❌ Missing RDS configuration in .env file")
            config_valid = False
        else:
            print(f"✅ RDS Host: {self.rds_host}")
            print(f"✅ RDS Database: {self.rds_database}")

        # Check SSH config
        if not self.ssh_host:
            print("❌ SSH_HOST not set in .env file")
            config_valid = False
        else:
            print(f"✅ SSH Host: {self.ssh_host}")
            print(f"✅ SSH User: {self.ssh_user}")

        # Check SSH key file
        if not os.path.exists(self.ssh_key_path):
            print(f"❌ SSH key not found: {self.ssh_key_path}")
            config_valid = False
        else:
            print(f"✅ SSH Key: {self.ssh_key_path}")

            # Check key permissions (should be 400 or 600)
            key_perms = oct(os.stat(self.ssh_key_path).st_mode)[-3:]
            if key_perms not in ['400', '600']:
                print(f"⚠️  Warning: SSH key has permissions {key_perms}")
                print(f"   Recommended: chmod 400 {self.ssh_key_path}")

        print(f"✅ Local Port: {self.local_port}")
        print(f"✅ Remote Port: {self.rds_port}")

        if not config_valid:
            print("\n❌ Configuration incomplete. Please update .env file.")
            return False

        print("\n✅ Configuration valid")
        return True

    def is_tunnel_running(self) -> Optional[int]:
        """Check if SSH tunnel is already running."""
        if not os.path.exists(self.pid_file):
            return None

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process is still running
            os.kill(pid, 0)
            return pid
        except (OSError, ValueError):
            # Process not running or invalid PID
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            return None

    def start_tunnel(self) -> bool:
        """Start SSH tunnel."""
        print("\n" + "=" * 60)
        print("STARTING SSH TUNNEL")
        print("=" * 60)

        # Check if tunnel already running
        existing_pid = self.is_tunnel_running()
        if existing_pid:
            print(f"⚠️  Tunnel already running (PID: {existing_pid})")
            return True

        # Build SSH command
        ssh_command = [
            'ssh',
            '-N',  # Don't execute remote command
            '-L', f'{self.local_port}:{self.rds_host}:{self.rds_port}',  # Local port forwarding
            '-i', self.ssh_key_path,  # SSH key
            '-o', 'StrictHostKeyChecking=no',  # Don't prompt for host verification
            '-o', 'ServerAliveInterval=60',  # Keep connection alive
            '-o', 'ServerAliveCountMax=3',  # Max keep-alive attempts
            f'{self.ssh_user}@{self.ssh_host}'
        ]

        print(f"Creating tunnel: localhost:{self.local_port} → {self.ssh_host} → {self.rds_host}:{self.rds_port}")

        try:
            # Start SSH tunnel in background
            process = subprocess.Popen(
                ssh_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )

            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))

            # Wait a bit to see if it fails immediately
            time.sleep(2)

            if process.poll() is not None:
                # Process exited
                _, stderr = process.communicate()
                print(f"❌ SSH tunnel failed to start:")
                print(stderr.decode())
                if os.path.exists(self.pid_file):
                    os.remove(self.pid_file)
                return False

            print(f"✅ SSH tunnel started successfully (PID: {process.pid})")
            print(f"\nConnection details:")
            print(f"   Local:  localhost:{self.local_port}")
            print(f"   Remote: {self.rds_host}:{self.rds_port}")
            print(f"   Via:    {self.ssh_user}@{self.ssh_host}")
            print(f"\n💡 Use RDS_HOST=localhost and RDS_PORT={self.local_port} to connect")
            return True

        except FileNotFoundError:
            print("❌ SSH command not found. Is OpenSSH installed?")
            return False
        except Exception as e:
            print(f"❌ Failed to start tunnel: {e}")
            return False

    def stop_tunnel(self) -> bool:
        """Stop SSH tunnel."""
        print("\n" + "=" * 60)
        print("STOPPING SSH TUNNEL")
        print("=" * 60)

        pid = self.is_tunnel_running()
        if not pid:
            print("⚠️  No tunnel running")
            return True

        try:
            # Kill the process group
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            time.sleep(1)

            # Check if it's still running
            try:
                os.kill(pid, 0)
                # Still running, force kill
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except OSError:
                pass

            # Remove PID file
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)

            print(f"✅ Tunnel stopped (PID: {pid})")
            return True

        except ProcessLookupError:
            print("⚠️  Process already terminated")
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            return True
        except Exception as e:
            print(f"❌ Failed to stop tunnel: {e}")
            return False

    def get_status(self) -> dict:
        """Get tunnel status."""
        pid = self.is_tunnel_running()

        status = {
            'running': pid is not None,
            'pid': pid,
            'local_port': self.local_port,
            'remote_host': self.rds_host,
            'remote_port': self.rds_port,
            'ssh_host': self.ssh_host
        }

        return status

    def print_status(self):
        """Print tunnel status."""
        print("\n" + "=" * 60)
        print("SSH TUNNEL STATUS")
        print("=" * 60)

        status = self.get_status()

        if status['running']:
            print(f"✅ Tunnel is RUNNING")
            print(f"   PID: {status['pid']}")
            print(f"   Local:  localhost:{status['local_port']}")
            print(f"   Remote: {status['remote_host']}:{status['remote_port']}")
            print(f"   Via:    {status['ssh_host']}")
        else:
            print("❌ Tunnel is NOT running")
            print(f"\nTo start: python scripts/ssh_tunnel_manager.py start")

    def test_connection(self) -> bool:
        """Test database connection through tunnel."""
        print("\n" + "=" * 60)
        print("TESTING CONNECTION THROUGH TUNNEL")
        print("=" * 60)

        # Check if tunnel is running
        if not self.is_tunnel_running():
            print("❌ Tunnel is not running")
            print("Start tunnel first: python scripts/ssh_tunnel_manager.py start")
            return False

        try:
            print(f"Connecting to: localhost:{self.local_port}/{self.rds_database}")

            # Connect through tunnel
            conn = psycopg2.connect(
                host='localhost',
                port=self.local_port,
                database=self.rds_database,
                user=self.rds_user,
                password=self.rds_password,
                connect_timeout=10
            )

            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]

            print(f"\n✅ Connection successful!")
            print(f"   PostgreSQL: {version[:60]}...")

            # Get table count
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public';
            """)
            table_count = cursor.fetchone()[0]
            print(f"   Tables: {table_count}")

            cursor.close()
            conn.close()

            print("\n✅ SSH tunnel is working correctly!")
            return True

        except psycopg2.OperationalError as e:
            print(f"\n❌ Connection failed: {e}")
            print("\nTroubleshooting:")
            print("   1. Verify tunnel is running")
            print("   2. Check EC2 security group allows SSH from your IP")
            print("   3. Check RDS security group allows EC2 → RDS on port 5432")
            print("   4. Verify SSH key has correct permissions (chmod 400)")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/ssh_tunnel_manager.py {start|stop|status|test}")
        print("\nCommands:")
        print("  start  - Start SSH tunnel")
        print("  stop   - Stop SSH tunnel")
        print("  status - Check tunnel status")
        print("  test   - Test connection through tunnel")
        sys.exit(1)

    command = sys.argv[1].lower()

    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  No .env file found!")
        print("Please create a .env file with SSH configuration.")
        print("See .env.example for reference.")
        sys.exit(1)

    manager = SSHTunnelManager()

    # Validate config for all commands except status
    if command != 'status':
        if not manager.validate_config():
            sys.exit(1)

    # Execute command
    if command == 'start':
        success = manager.start_tunnel()
        sys.exit(0 if success else 1)

    elif command == 'stop':
        success = manager.stop_tunnel()
        sys.exit(0 if success else 1)

    elif command == 'status':
        manager.print_status()
        sys.exit(0)

    elif command == 'test':
        success = manager.test_connection()
        sys.exit(0 if success else 1)

    else:
        print(f"❌ Unknown command: {command}")
        print("Valid commands: start, stop, status, test")
        sys.exit(1)


if __name__ == "__main__":
    main()
