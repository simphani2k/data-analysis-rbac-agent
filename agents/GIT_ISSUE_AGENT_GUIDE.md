# Git Issue Agent - Claude Code Integration Guide

A Python agent for GitHub issue CRUD operations, designed for use with Claude Code.

## Quick Start for Claude

```python
from agents.git_issue_agent import GitIssueAgent, IssueState

# Initialize
agent = GitIssueAgent()  # Uses current repo

# Common operations
issues = agent.list_issues()
issue = agent.get_issue(42)
new_issue = agent.create_issue("Title", body="Description", labels=["bug"])
agent.update_issue(42, add_labels=["priority-high"])
agent.close_issue(42, comment="Fixed")
```

## Core CRUD Operations

### CREATE
```python
# Basic creation
issue = agent.create_issue(
    title="Bug: Login fails on mobile",
    body="Users report login failures",
    labels=["bug", "mobile"],
    assignees=["username"]
)

# With milestone and project
issue = agent.create_issue(
    title="Feature: Dark mode",
    body="Add dark mode support",
    labels=["feature", "ui"],
    milestone="v2.0",
    project="Frontend"
)
```

### READ
```python
# List issues with filters
open_issues = agent.list_issues(state=IssueState.OPEN, limit=50)
bugs = agent.list_issues(labels=["bug"])
my_issues = agent.list_issues(assignee="username")

# Get specific issue
issue = agent.get_issue(42)
print(f"{issue.number}: {issue.title} [{issue.state}]")
print(f"Labels: {', '.join(issue.labels)}")

# Search with GitHub syntax
auth_issues = agent.search_issues("authentication in:title is:open")
old_bugs = agent.search_issues("is:open label:bug created:<2024-01-01")
```

### UPDATE
```python
# Update title and body
agent.update_issue(42, title="New Title", body="New description")

# Manage labels
agent.update_issue(42, add_labels=["priority-high", "needs-review"])
agent.update_issue(42, remove_labels=["needs-triage"])

# Manage assignees
agent.update_issue(42, add_assignees=["dev1", "dev2"])

# Add comment
agent.add_comment(42, "Working on this issue")

# Close/reopen
agent.close_issue(42, comment="Fixed in PR #123")
agent.reopen_issue(42, comment="Issue persists")
```

### DELETE
```python
# Delete requires explicit confirmation
agent.delete_issue(42, confirm=True)  # ⚠️ Permanent!
```

## Issue Object Structure

```python
@dataclass
class Issue:
    number: int          # Issue number
    title: str          # Title
    state: str          # "OPEN" or "CLOSED"
    body: str           # Description
    labels: List[str]   # Label names
    assignees: List[str] # Usernames
    url: str            # GitHub URL
```

## Common Use Cases for Claude Code

### 1. Bulk Issue Creation from Tasks
```python
agent = GitIssueAgent()

tasks = [
    {"title": "Build AWS backend", "labels": ["backend", "aws"]},
    {"title": "Create Next.js UI", "labels": ["frontend"]},
    {"title": "Integrate frontend/backend", "labels": ["integration"]}
]

created = []
for task in tasks:
    issue = agent.create_issue(**task)
    created.append(issue)
    print(f"✅ Created #{issue.number}: {issue.title}")
```

### 2. Issue Analysis and Reporting
```python
agent = GitIssueAgent()

# Get all open issues
issues = agent.list_issues(state=IssueState.OPEN, limit=100)

# Analyze by category
bugs = [i for i in issues if "bug" in i.labels]
features = [i for i in issues if "feature" in i.labels]
unlabeled = [i for i in issues if not i.labels]

print(f"📊 Issue Summary:")
print(f"Total Open: {len(issues)}")
print(f"Bugs: {len(bugs)}")
print(f"Features: {len(features)}")
print(f"Needs Triage: {len(unlabeled)}")
```

### 3. Automated Triage
```python
agent = GitIssueAgent()

# Find unlabeled issues
issues = agent.list_issues(state=IssueState.OPEN)
unlabeled = [i for i in issues if not i.labels]

# Add triage label
for issue in unlabeled:
    agent.update_issue(
        issue.number,
        add_labels=["needs-triage"],
        add_assignees=["triage-team"]
    )
    print(f"🏷️  Triaged #{issue.number}")
```

### 4. Issue Dependency Tracking
```python
agent = GitIssueAgent()

# Create parent issue
parent = agent.create_issue(
    title="Epic: User Authentication System",
    body="Complete authentication system implementation",
    labels=["epic"]
)

# Create child issues with references
subtasks = [
    "Implement JWT tokens",
    "Add password reset flow",
    "Create login UI"
]

for task in subtasks:
    child = agent.create_issue(
        title=task,
        body=f"Part of #{parent.number}",
        labels=["subtask"]
    )
    # Add reference in parent
    agent.add_comment(parent.number, f"Subtask created: #{child.number}")
```

### 5. Close Completed Issues
```python
agent = GitIssueAgent()

# Find issues mentioned in recent commits
# (Would need git log parsing - simplified here)
resolved_issue_numbers = [12, 15, 23]

for num in resolved_issue_numbers:
    agent.close_issue(
        num,
        comment="✅ Completed and merged to main"
    )
```

## Utility Operations

```python
# Pin important issues
agent.pin_issue(42)

# Lock resolved discussions
agent.lock_issue(42, reason="resolved")

# Unlock if needed
agent.unlock_issue(42)

# Unpin
agent.unpin_issue(42)
```

## Error Handling

```python
try:
    issue = agent.get_issue(999999)
except RuntimeError as e:
    print(f"❌ Error: {e}")
    # Handle error appropriately
```

## Prerequisites

1. Install GitHub CLI: `brew install gh` (macOS)
2. Authenticate: `gh auth login`
3. Make script executable: `chmod +x agents/git_issue_agent.py`

## Working with Multiple Repos

```python
# Specify different repos
backend = GitIssueAgent(repo="owner/backend")
frontend = GitIssueAgent(repo="owner/frontend")

# Create related issues
be_issue = backend.create_issue("Add API endpoint")
fe_issue = frontend.create_issue(
    "Connect to API",
    body=f"Backend: {be_issue.url}"
)
```

## Advanced Search Queries

```python
# Complex GitHub search syntax
results = agent.search_issues(
    "is:open label:bug -label:wontfix created:>2024-01-01"
)

# Find stale issues
stale = agent.search_issues(
    "is:open updated:<2024-06-01 no:assignee"
)

# Find issues by author
my_issues = agent.search_issues("is:open author:@me")
```

## Integration with Claude Code Workflows

### Scenario: Convert TODO comments to issues
```python
# After analyzing code with TODOs
agent = GitIssueAgent()

todos = [
    {"file": "auth.py", "line": 45, "text": "Add rate limiting"},
    {"file": "api.py", "line": 102, "text": "Improve error handling"}
]

for todo in todos:
    issue = agent.create_issue(
        title=f"TODO: {todo['text']}",
        body=f"Found in `{todo['file']}:{todo['line']}`\n\n{todo['text']}",
        labels=["tech-debt", "from-code"]
    )
    print(f"📝 Created issue #{issue.number} for {todo['file']}")
```

### Scenario: Create issues from test failures
```python
# After test run analysis
agent = GitIssueAgent()

failures = [
    {"test": "test_login", "error": "Connection timeout"},
    {"test": "test_signup", "error": "Validation failed"}
]

for failure in failures:
    issue = agent.create_issue(
        title=f"Test Failure: {failure['test']}",
        body=f"```\n{failure['error']}\n```",
        labels=["bug", "test-failure", "needs-investigation"]
    )
    print(f"🐛 Created #{issue.number} for {failure['test']}")
```

## Best Practices

1. **Always use confirm=True for deletions** - They're permanent
2. **Add meaningful comments** when closing issues
3. **Use labels consistently** for better organization
4. **Link related issues** in descriptions
5. **Search before creating** to avoid duplicates
6. **Use milestones** for release planning
7. **Assign issues** to track ownership

## Quick Reference

| Operation | Method | Example |
|-----------|--------|---------|
| Create | `create_issue()` | `agent.create_issue("Title")` |
| List | `list_issues()` | `agent.list_issues(state=IssueState.OPEN)` |
| Get | `get_issue()` | `agent.get_issue(42)` |
| Search | `search_issues()` | `agent.search_issues("bug in:title")` |
| Update | `update_issue()` | `agent.update_issue(42, title="New")` |
| Comment | `add_comment()` | `agent.add_comment(42, "text")` |
| Close | `close_issue()` | `agent.close_issue(42)` |
| Reopen | `reopen_issue()` | `agent.reopen_issue(42)` |
| Delete | `delete_issue()` | `agent.delete_issue(42, confirm=True)` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `command not found: gh` | GitHub CLI not installed | `brew install gh` |
| `authentication required` | Not logged in | `gh auth login` |
| `issue not found` | Invalid issue number | Verify number exists |
| `permission denied` | No repo access | Check permissions |
| `requires confirmation` | Delete without confirm | Add `confirm=True` |
