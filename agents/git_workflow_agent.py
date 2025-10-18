#!/usr/bin/env python3
"""
Git Workflow Agent - Git operations for branches, commits, and PRs
Handles branch management, commits, pull requests, and common git operations
"""

import subprocess
import json
import re
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class BranchType(Enum):
    """Branch type enumeration"""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    HOTFIX = "hotfix"
    RELEASE = "release"
    CHORE = "chore"


@dataclass
class Branch:
    """Branch data structure"""
    name: str
    current: bool
    remote: bool = False
    tracking: Optional[str] = None
    commit: Optional[str] = None


@dataclass
class Commit:
    """Commit data structure"""
    sha: str
    message: str
    author: str
    date: str
    short_sha: str = ""

    def __post_init__(self):
        if not self.short_sha:
            self.short_sha = self.sha[:7]


@dataclass
class PullRequest:
    """Pull Request data structure"""
    number: int
    title: str
    state: str
    source_branch: str
    target_branch: str
    url: str
    mergeable: Optional[bool] = None


class GitWorkflowAgent:
    """Agent for managing Git workflow operations"""

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize the Git Workflow Agent

        Args:
            repo_path: Path to git repository. If None, uses current directory
        """
        self.repo_path = repo_path
        self._check_git_installed()
        self._check_gh_installed()

    def _check_git_installed(self) -> None:
        """Check if Git is installed"""
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
                text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Git is not installed")

    def _check_gh_installed(self) -> None:
        """Check if GitHub CLI is installed"""
        try:
            subprocess.run(
                ["gh", "--version"],
                check=True,
                capture_output=True,
                text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "GitHub CLI (gh) is not installed. Install from: https://cli.github.com/"
            )

    def _run_git_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a git command and return output

        Args:
            args: Command arguments to pass to git
            check: Whether to raise exception on non-zero exit

        Returns:
            Command output as string
        """
        cmd = ["git"]
        if self.repo_path:
            cmd.extend(["-C", self.repo_path])
        cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command error: {e.stderr.strip()}")

    def _run_gh_command(self, args: List[str]) -> str:
        """
        Run a gh command and return output

        Args:
            args: Command arguments to pass to gh

        Returns:
            Command output as string
        """
        cmd = ["gh"] + args

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"GitHub CLI error: {e.stderr.strip()}")

    # BRANCH operations

    def create_branch(
        self,
        branch_name: str,
        branch_type: Optional[BranchType] = None,
        from_branch: Optional[str] = None,
        switch: bool = True
    ) -> Branch:
        """
        Create a new branch

        Args:
            branch_name: Name of the branch (without prefix)
            branch_type: Type of branch (adds prefix like feature/, bugfix/)
            from_branch: Branch to create from (default: current branch)
            switch: Whether to switch to the new branch

        Returns:
            Created Branch object
        """
        # Build full branch name with prefix if type provided
        if branch_type:
            full_name = f"{branch_type.value}/{branch_name}"
        else:
            full_name = branch_name

        # Create branch from specific branch if specified
        if from_branch:
            self._run_git_command(["checkout", from_branch])

        # Create and optionally switch to branch
        if switch:
            self._run_git_command(["checkout", "-b", full_name])
        else:
            self._run_git_command(["branch", full_name])

        return self.get_current_branch()

    def switch_branch(self, branch_name: str) -> Branch:
        """
        Switch to an existing branch

        Args:
            branch_name: Name of the branch to switch to

        Returns:
            Branch object for the switched-to branch
        """
        self._run_git_command(["checkout", branch_name])
        return self.get_current_branch()

    def delete_branch(self, branch_name: str, force: bool = False) -> None:
        """
        Delete a branch

        Args:
            branch_name: Name of the branch to delete
            force: Force delete even if not merged
        """
        flag = "-D" if force else "-d"
        self._run_git_command(["branch", flag, branch_name])

    def list_branches(self, include_remote: bool = False) -> List[Branch]:
        """
        List all branches

        Args:
            include_remote: Include remote branches

        Returns:
            List of Branch objects
        """
        args = ["branch", "-v"]
        if include_remote:
            args.append("-a")

        output = self._run_git_command(args)
        branches = []

        for line in output.split('\n'):
            if not line.strip():
                continue

            current = line.startswith('*')
            line = line.lstrip('* ').strip()
            parts = line.split()

            if len(parts) >= 2:
                name = parts[0]
                commit = parts[1]
                remote = name.startswith('remotes/')

                branches.append(Branch(
                    name=name,
                    current=current,
                    remote=remote,
                    commit=commit
                ))

        return branches

    def get_current_branch(self) -> Branch:
        """
        Get the current branch

        Returns:
            Branch object for current branch
        """
        name = self._run_git_command(["branch", "--show-current"])

        # Get tracking info
        tracking = None
        try:
            tracking = self._run_git_command(
                ["rev-parse", "--abbrev-ref", f"{name}@{{upstream}}"],
                check=False
            )
        except:
            pass

        return Branch(
            name=name,
            current=True,
            tracking=tracking if tracking else None
        )

    # COMMIT operations

    def stage_files(self, files: Optional[List[str]] = None) -> None:
        """
        Stage files for commit

        Args:
            files: List of file paths to stage. If None, stages all changes
        """
        if files:
            self._run_git_command(["add"] + files)
        else:
            self._run_git_command(["add", "-A"])

    def commit(
        self,
        message: str,
        files: Optional[List[str]] = None,
        amend: bool = False,
        allow_empty: bool = False
    ) -> Commit:
        """
        Create a commit

        Args:
            message: Commit message
            files: Files to stage and commit. If None, commits staged files
            amend: Amend previous commit
            allow_empty: Allow empty commit

        Returns:
            Commit object
        """
        # Stage files if provided
        if files:
            self.stage_files(files)

        # Build commit command
        args = ["commit", "-m", message]

        if amend:
            args.append("--amend")

        if allow_empty:
            args.append("--allow-empty")

        self._run_git_command(args)

        # Get the commit details
        return self.get_last_commit()

    def commit_with_issue(
        self,
        message: str,
        issue_number: int,
        files: Optional[List[str]] = None
    ) -> Commit:
        """
        Create a commit with issue reference

        Args:
            message: Commit message
            issue_number: Issue number to reference
            files: Files to stage and commit

        Returns:
            Commit object
        """
        full_message = f"{message}\n\nRelated to #{issue_number}"
        return self.commit(full_message, files=files)

    def get_last_commit(self) -> Commit:
        """
        Get the last commit

        Returns:
            Commit object
        """
        output = self._run_git_command([
            "log", "-1",
            "--format=%H%n%s%n%an%n%ai"
        ])

        lines = output.split('\n')
        if len(lines) >= 4:
            return Commit(
                sha=lines[0],
                message=lines[1],
                author=lines[2],
                date=lines[3]
            )

        raise RuntimeError("Could not parse commit information")

    def get_commit_history(self, limit: int = 10) -> List[Commit]:
        """
        Get commit history

        Args:
            limit: Maximum number of commits to retrieve

        Returns:
            List of Commit objects
        """
        output = self._run_git_command([
            "log", f"-{limit}",
            "--format=%H|%s|%an|%ai"
        ])

        commits = []
        for line in output.split('\n'):
            if not line.strip():
                continue

            parts = line.split('|')
            if len(parts) >= 4:
                commits.append(Commit(
                    sha=parts[0],
                    message=parts[1],
                    author=parts[2],
                    date=parts[3]
                ))

        return commits

    def push(
        self,
        branch: Optional[str] = None,
        set_upstream: bool = False,
        force: bool = False
    ) -> None:
        """
        Push commits to remote

        Args:
            branch: Branch to push (default: current branch)
            set_upstream: Set upstream tracking
            force: Force push
        """
        args = ["push"]

        if force:
            args.append("--force")

        if set_upstream:
            # Get current branch if not specified
            if not branch:
                branch = self.get_current_branch().name
            args.extend(["--set-upstream", "origin", branch])
        elif branch:
            args.append(branch)

        self._run_git_command(args)

    def pull(self, rebase: bool = False) -> None:
        """
        Pull changes from remote

        Args:
            rebase: Use rebase instead of merge
        """
        args = ["pull"]
        if rebase:
            args.append("--rebase")

        self._run_git_command(args)

    # PULL REQUEST operations

    def create_pr(
        self,
        title: str,
        body: Optional[str] = None,
        base: str = "main",
        draft: bool = False,
        auto_fill: bool = False
    ) -> PullRequest:
        """
        Create a pull request

        Args:
            title: PR title
            body: PR description
            base: Target branch (default: main)
            draft: Create as draft PR
            auto_fill: Auto-fill title/body from commits

        Returns:
            PullRequest object
        """
        args = ["pr", "create", "--base", base, "--title", title]

        if body:
            args.extend(["--body", body])

        if draft:
            args.append("--draft")

        if auto_fill:
            args.append("--fill")

        # Create PR and get URL
        output = self._run_gh_command(args)

        # Extract PR number from URL
        match = re.search(r'/pull/(\d+)', output)
        if not match:
            raise RuntimeError(f"Could not parse PR number from: {output}")

        pr_number = int(match.group(1))

        # Get PR details
        return self.get_pr(pr_number)

    def create_pr_from_issue(
        self,
        issue_number: int,
        base: str = "main",
        draft: bool = False
    ) -> PullRequest:
        """
        Create a PR that closes an issue

        Args:
            issue_number: Issue number to reference
            base: Target branch
            draft: Create as draft PR

        Returns:
            PullRequest object
        """
        current = self.get_current_branch()

        # Get issue title for PR title
        issue_info = self._run_gh_command([
            "issue", "view", str(issue_number),
            "--json", "title"
        ])
        issue_data = json.loads(issue_info)

        title = f"Fix #{issue_number}: {issue_data['title']}"
        body = f"Closes #{issue_number}"

        return self.create_pr(title, body=body, base=base, draft=draft)

    def list_prs(
        self,
        state: str = "open",
        limit: int = 30
    ) -> List[PullRequest]:
        """
        List pull requests

        Args:
            state: PR state (open, closed, merged, all)
            limit: Maximum number of PRs to return

        Returns:
            List of PullRequest objects
        """
        output = self._run_gh_command([
            "pr", "list",
            "--state", state,
            "--limit", str(limit),
            "--json", "number,title,state,headRefName,baseRefName,url"
        ])

        data = json.loads(output)

        return [
            PullRequest(
                number=pr["number"],
                title=pr["title"],
                state=pr["state"],
                source_branch=pr["headRefName"],
                target_branch=pr["baseRefName"],
                url=pr["url"]
            )
            for pr in data
        ]

    def get_pr(self, pr_number: int) -> PullRequest:
        """
        Get a specific pull request

        Args:
            pr_number: PR number

        Returns:
            PullRequest object
        """
        output = self._run_gh_command([
            "pr", "view", str(pr_number),
            "--json", "number,title,state,headRefName,baseRefName,url,mergeable"
        ])

        pr = json.loads(output)

        return PullRequest(
            number=pr["number"],
            title=pr["title"],
            state=pr["state"],
            source_branch=pr["headRefName"],
            target_branch=pr["baseRefName"],
            url=pr["url"],
            mergeable=pr.get("mergeable")
        )

    def merge_pr(
        self,
        pr_number: int,
        method: str = "merge",
        delete_branch: bool = True
    ) -> None:
        """
        Merge a pull request

        Args:
            pr_number: PR number to merge
            method: Merge method (merge, squash, rebase)
            delete_branch: Delete branch after merge
        """
        args = ["pr", "merge", str(pr_number), f"--{method}"]

        if delete_branch:
            args.append("--delete-branch")

        self._run_gh_command(args)

    def close_pr(self, pr_number: int, comment: Optional[str] = None) -> None:
        """
        Close a pull request without merging

        Args:
            pr_number: PR number to close
            comment: Optional closing comment
        """
        args = ["pr", "close", str(pr_number)]

        if comment:
            args.extend(["--comment", comment])

        self._run_gh_command(args)

    # STATUS and DIFF operations

    def get_status(self, short: bool = False) -> str:
        """
        Get repository status

        Args:
            short: Use short format

        Returns:
            Status output
        """
        args = ["status"]
        if short:
            args.append("--short")

        return self._run_git_command(args)

    def get_diff(
        self,
        staged: bool = False,
        files: Optional[List[str]] = None
    ) -> str:
        """
        Get diff of changes

        Args:
            staged: Show staged changes
            files: Specific files to diff

        Returns:
            Diff output
        """
        args = ["diff"]

        if staged:
            args.append("--staged")

        if files:
            args.extend(files)

        return self._run_git_command(args)

    def has_changes(self) -> bool:
        """
        Check if there are uncommitted changes

        Returns:
            True if there are changes
        """
        status = self._run_git_command(["status", "--porcelain"])
        return bool(status.strip())

    def get_changed_files(self, staged: bool = False) -> List[str]:
        """
        Get list of changed files

        Args:
            staged: Only show staged files

        Returns:
            List of file paths
        """
        args = ["diff", "--name-only"]
        if staged:
            args.append("--staged")

        output = self._run_git_command(args)
        return [f for f in output.split('\n') if f.strip()]

    # STASH operations

    def stash_save(self, message: Optional[str] = None, include_untracked: bool = False) -> None:
        """
        Stash current changes

        Args:
            message: Stash message
            include_untracked: Include untracked files
        """
        args = ["stash", "push"]

        if message:
            args.extend(["-m", message])

        if include_untracked:
            args.append("-u")

        self._run_git_command(args)

    def stash_pop(self) -> None:
        """Pop the most recent stash"""
        self._run_git_command(["stash", "pop"])

    def stash_list(self) -> List[str]:
        """
        List all stashes

        Returns:
            List of stash descriptions
        """
        output = self._run_git_command(["stash", "list"])
        return [line for line in output.split('\n') if line.strip()]

    # UTILITY operations

    def get_remote_url(self) -> str:
        """
        Get the remote repository URL

        Returns:
            Remote URL
        """
        return self._run_git_command(["remote", "get-url", "origin"])

    def get_repo_info(self) -> Dict[str, str]:
        """
        Get repository information

        Returns:
            Dictionary with repo info
        """
        remote_url = self.get_remote_url()
        current_branch = self.get_current_branch()
        has_changes = self.has_changes()

        return {
            "remote_url": remote_url,
            "current_branch": current_branch.name,
            "has_changes": has_changes,
            "tracking": current_branch.tracking
        }

    def is_clean(self) -> bool:
        """
        Check if working directory is clean

        Returns:
            True if no uncommitted changes
        """
        return not self.has_changes()


def main():
    """CLI interface for the Git Workflow Agent"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: git_workflow_agent.py <command> [args]")
        print("\nCommands:")
        print("  create-branch <name> [--type feature|bugfix]")
        print("  switch <branch>")
        print("  commit <message>")
        print("  push")
        print("  create-pr <title>")
        print("  status")
        sys.exit(1)

    agent = GitWorkflowAgent()
    command = sys.argv[1]

    try:
        if command == "create-branch":
            branch = agent.create_branch(sys.argv[2])
            print(f"Created and switched to branch: {branch.name}")

        elif command == "switch":
            branch = agent.switch_branch(sys.argv[2])
            print(f"Switched to branch: {branch.name}")

        elif command == "commit":
            commit = agent.commit(sys.argv[2])
            print(f"Created commit: {commit.short_sha} - {commit.message}")

        elif command == "push":
            agent.push(set_upstream=True)
            print("Pushed to remote")

        elif command == "create-pr":
            pr = agent.create_pr(sys.argv[2])
            print(f"Created PR #{pr.number}: {pr.url}")

        elif command == "status":
            print(agent.get_status())

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
