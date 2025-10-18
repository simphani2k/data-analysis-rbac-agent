#!/usr/bin/env python3
"""
Git Issue Agent - CRUD operations for GitHub Issues
Handles Create, Read, Update, Delete operations for GitHub issues via GitHub CLI (gh)
"""

import subprocess
import json
import re
import sys
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class IssueState(Enum):
    """Issue state enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    ALL = "all"


@dataclass
class Issue:
    """Issue data structure"""
    number: int
    title: str
    state: str
    body: str = ""
    labels: List[str] = None
    assignees: List[str] = None
    url: str = ""

    def __post_init__(self):
        if self.labels is None:
            self.labels = []
        if self.assignees is None:
            self.assignees = []


class GitIssueAgent:
    """Agent for managing GitHub issues via gh CLI"""

    def __init__(self, repo: Optional[str] = None):
        """
        Initialize the Git Issue Agent

        Args:
            repo: Repository in format 'owner/repo'. If None, uses current directory's repo
        """
        self.repo = repo
        self._check_gh_installed()

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

    def _run_gh_command(self, args: List[str]) -> str:
        """
        Run a gh command and return output

        Args:
            args: Command arguments to pass to gh

        Returns:
            Command output as string
        """
        cmd = ["gh"] + args
        if self.repo:
            cmd.extend(["-R", self.repo])

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"GitHub CLI error: {e.stderr.strip()}")

    # CREATE operations

    def create_issue(
        self,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[str] = None,
        project: Optional[str] = None
    ) -> Issue:
        """
        Create a new GitHub issue

        Args:
            title: Issue title (required)
            body: Issue body/description
            labels: List of label names to apply
            assignees: List of usernames to assign
            milestone: Milestone name or number
            project: Project name or number

        Returns:
            Created Issue object
        """
        args = ["issue", "create", "--title", title]

        if body:
            args.extend(["--body", body])

        if labels:
            args.extend(["--label", ",".join(labels)])

        if assignees:
            args.extend(["--assignee", ",".join(assignees)])

        if milestone:
            args.extend(["--milestone", milestone])

        if project:
            args.extend(["--project", project])

        # Create the issue and get the URL
        output = self._run_gh_command(args)

        # Extract issue number from URL (output format: https://github.com/owner/repo/issues/123)
        match = re.search(r'/issues/(\d+)', output)
        if not match:
            raise RuntimeError(f"Could not parse issue number from output: {output}")

        issue_number = int(match.group(1))

        # Fetch the full issue details
        return self.get_issue(issue_number)

    # READ operations

    def list_issues(
        self,
        state: IssueState = IssueState.OPEN,
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        limit: int = 30
    ) -> List[Issue]:
        """
        List issues with optional filters

        Args:
            state: Filter by state (open, closed, all)
            labels: Filter by label names
            assignee: Filter by assignee username
            limit: Maximum number of issues to return

        Returns:
            List of Issue objects
        """
        args = [
            "issue", "list",
            "--state", state.value,
            "--limit", str(limit),
            "--json", "number,title,body,state,labels,assignees,url"
        ]

        if labels:
            args.extend(["--label", ",".join(labels)])

        if assignee:
            args.extend(["--assignee", assignee])

        output = self._run_gh_command(args)
        data = json.loads(output)

        return [
            Issue(
                number=item["number"],
                title=item["title"],
                state=item["state"],
                body=item.get("body", ""),
                labels=[label["name"] for label in item.get("labels", [])],
                assignees=[assignee["login"] for assignee in item.get("assignees", [])],
                url=item.get("url", "")
            )
            for item in data
        ]

    def get_issue(self, issue_number: int) -> Issue:
        """
        Get a specific issue by number

        Args:
            issue_number: Issue number

        Returns:
            Issue object
        """
        args = [
            "issue", "view", str(issue_number),
            "--json", "number,title,body,state,labels,assignees,url"
        ]

        output = self._run_gh_command(args)
        data = json.loads(output)

        return Issue(
            number=data["number"],
            title=data["title"],
            state=data["state"],
            body=data.get("body", ""),
            labels=[label["name"] for label in data.get("labels", [])],
            assignees=[assignee["login"] for assignee in data.get("assignees", [])],
            url=data.get("url", "")
        )

    def search_issues(self, query: str, limit: int = 30) -> List[Issue]:
        """
        Search issues using GitHub search syntax

        Args:
            query: Search query (e.g., "authentication in:title")
            limit: Maximum number of results

        Returns:
            List of Issue objects
        """
        args = [
            "issue", "list",
            "--search", query,
            "--limit", str(limit),
            "--json", "number,title,body,state,labels,assignees,url"
        ]

        output = self._run_gh_command(args)
        data = json.loads(output)

        return [
            Issue(
                number=item["number"],
                title=item["title"],
                state=item["state"],
                body=item.get("body", ""),
                labels=[label["name"] for label in item.get("labels", [])],
                assignees=[assignee["login"] for assignee in item.get("assignees", [])],
                url=item.get("url", "")
            )
            for item in data
        ]

    # UPDATE operations

    def update_issue(
        self,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
        add_assignees: Optional[List[str]] = None,
        remove_assignees: Optional[List[str]] = None,
        milestone: Optional[str] = None
    ) -> Issue:
        """
        Update an existing issue

        Args:
            issue_number: Issue number to update
            title: New title
            body: New body
            add_labels: Labels to add
            remove_labels: Labels to remove
            add_assignees: Assignees to add
            remove_assignees: Assignees to remove
            milestone: Milestone to set

        Returns:
            Updated Issue object
        """
        args = ["issue", "edit", str(issue_number)]

        if title:
            args.extend(["--title", title])

        if body:
            args.extend(["--body", body])

        if add_labels:
            args.extend(["--add-label", ",".join(add_labels)])

        if remove_labels:
            args.extend(["--remove-label", ",".join(remove_labels)])

        if add_assignees:
            args.extend(["--add-assignee", ",".join(add_assignees)])

        if remove_assignees:
            args.extend(["--remove-assignee", ",".join(remove_assignees)])

        if milestone:
            args.extend(["--milestone", milestone])

        self._run_gh_command(args)

        # Return updated issue
        return self.get_issue(issue_number)

    def close_issue(self, issue_number: int, comment: Optional[str] = None) -> Issue:
        """
        Close an issue

        Args:
            issue_number: Issue number to close
            comment: Optional closing comment

        Returns:
            Closed Issue object
        """
        args = ["issue", "close", str(issue_number)]

        if comment:
            args.extend(["--comment", comment])

        self._run_gh_command(args)
        return self.get_issue(issue_number)

    def reopen_issue(self, issue_number: int, comment: Optional[str] = None) -> Issue:
        """
        Reopen a closed issue

        Args:
            issue_number: Issue number to reopen
            comment: Optional reopening comment

        Returns:
            Reopened Issue object
        """
        args = ["issue", "reopen", str(issue_number)]

        if comment:
            args.extend(["--comment", comment])

        self._run_gh_command(args)
        return self.get_issue(issue_number)

    def add_comment(self, issue_number: int, comment: str) -> None:
        """
        Add a comment to an issue

        Args:
            issue_number: Issue number
            comment: Comment text
        """
        args = ["issue", "comment", str(issue_number), "--body", comment]
        self._run_gh_command(args)

    # DELETE operations

    def delete_issue(self, issue_number: int, confirm: bool = False) -> None:
        """
        Delete an issue (WARNING: This is permanent and requires confirmation)

        Args:
            issue_number: Issue number to delete
            confirm: Must be True to actually delete
        """
        if not confirm:
            raise ValueError(
                "Issue deletion requires explicit confirmation. Set confirm=True"
            )

        args = ["issue", "delete", str(issue_number), "--yes"]
        self._run_gh_command(args)

    # UTILITY operations

    def pin_issue(self, issue_number: int) -> None:
        """Pin an issue to the repository"""
        args = ["issue", "pin", str(issue_number)]
        self._run_gh_command(args)

    def unpin_issue(self, issue_number: int) -> None:
        """Unpin an issue from the repository"""
        args = ["issue", "unpin", str(issue_number)]
        self._run_gh_command(args)

    def lock_issue(self, issue_number: int, reason: Optional[str] = None) -> None:
        """
        Lock an issue conversation

        Args:
            issue_number: Issue number to lock
            reason: Lock reason (off-topic, too heated, resolved, spam)
        """
        args = ["issue", "lock", str(issue_number)]

        if reason:
            args.extend(["--reason", reason])

        self._run_gh_command(args)

    def unlock_issue(self, issue_number: int) -> None:
        """Unlock an issue conversation"""
        args = ["issue", "unlock", str(issue_number)]
        self._run_gh_command(args)


def main():
    """CLI interface for the Git Issue Agent"""
    if len(sys.argv) < 2:
        print("Usage: git_issue_agent.py <command> [args]")
        print("\nCommands:")
        print("  create <title> [--body <text>] [--labels <l1,l2>]")
        print("  list [--state open|closed|all] [--limit N]")
        print("  get <issue_number>")
        print("  update <issue_number> [--title <text>] [--body <text>]")
        print("  close <issue_number> [--comment <text>]")
        print("  reopen <issue_number>")
        print("  delete <issue_number> --confirm")
        sys.exit(1)

    agent = GitIssueAgent()
    command = sys.argv[1]

    try:
        if command == "create":
            issue = agent.create_issue(title=sys.argv[2])
            print(f"Created issue #{issue.number}: {issue.title}")
            print(f"URL: {issue.url}")

        elif command == "list":
            issues = agent.list_issues()
            for issue in issues:
                print(f"#{issue.number}: {issue.title} [{issue.state}]")

        elif command == "get":
            issue = agent.get_issue(int(sys.argv[2]))
            print(f"Issue #{issue.number}: {issue.title}")
            print(f"State: {issue.state}")
            print(f"URL: {issue.url}")
            print(f"\n{issue.body}")

        elif command == "close":
            issue = agent.close_issue(int(sys.argv[2]))
            print(f"Closed issue #{issue.number}")

        elif command == "delete":
            if "--confirm" in sys.argv:
                agent.delete_issue(int(sys.argv[2]), confirm=True)
                print(f"Deleted issue #{sys.argv[2]}")
            else:
                print("Add --confirm to actually delete the issue")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
