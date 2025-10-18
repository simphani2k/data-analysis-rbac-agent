# Git Workflow Agent - Claude Code Integration Guide

A Python agent for Git workflow operations: branches, commits, PRs, and version control management.

## Quick Start for Claude

```python
from agents.git_workflow_agent import GitWorkflowAgent, BranchType

# Initialize
agent = GitWorkflowAgent()  # Uses current directory

# Common operations
agent.create_branch("fix-login", branch_type=BranchType.BUGFIX)
agent.commit("Fixed login validation")
agent.push(set_upstream=True)
pr = agent.create_pr("Fix login issue")
```

## Core Operations

### BRANCH Management

```python
# Create and switch to new branch
branch = agent.create_branch(
    "auth-system",
    branch_type=BranchType.FEATURE  # Creates: feature/auth-system
)

# Create branch without switching
branch = agent.create_branch("test-branch", switch=False)

# Create from specific branch
branch = agent.create_branch("hotfix", branch_type=BranchType.HOTFIX, from_branch="main")

# Switch branches
agent.switch_branch("main")
agent.switch_branch("feature/auth-system")

# List all branches
branches = agent.list_branches()
for branch in branches:
    marker = "* " if branch.current else "  "
    print(f"{marker}{branch.name}")

# Get current branch
current = agent.get_current_branch()
print(f"On branch: {current.name}")

# Delete branch
agent.delete_branch("old-feature")
agent.delete_branch("experimental", force=True)  # Force delete
```

### COMMIT Operations

```python
# Stage and commit specific files
agent.stage_files(["auth.py", "login.py"])
commit = agent.commit("Added authentication")

# Stage all and commit
agent.commit("Fixed all bugs")  # Auto-stages all changes

# Commit with files in one call
commit = agent.commit("Updated config", files=["config.json"])

# Commit with issue reference
commit = agent.commit_with_issue(
    "Fixed login validation",
    issue_number=5
)  # Adds "Related to #5" to commit message

# Amend previous commit
commit = agent.commit("Updated message", amend=True)

# Get last commit
last = agent.get_last_commit()
print(f"{last.short_sha}: {last.message} by {last.author}")

# Get commit history
commits = agent.get_commit_history(limit=10)
for c in commits:
    print(f"{c.short_sha} - {c.message}")
```

### PUSH/PULL Operations

```python
# Push to remote
agent.push()

# Push and set upstream
agent.push(set_upstream=True)

# Push specific branch
agent.push(branch="feature/new-feature", set_upstream=True)

# Force push (use carefully!)
agent.push(force=True)

# Pull from remote
agent.pull()

# Pull with rebase
agent.pull(rebase=True)
```

### PULL REQUEST Operations

```python
# Create basic PR
pr = agent.create_pr(
    title="Add authentication system",
    body="Implements JWT authentication with refresh tokens",
    base="main"
)
print(f"Created PR #{pr.number}: {pr.url}")

# Create draft PR
pr = agent.create_pr("WIP: New feature", draft=True)

# Create PR from issue
pr = agent.create_pr_from_issue(
    issue_number=5,
    base="main"
)  # Auto-fills title and adds "Closes #5"

# List PRs
open_prs = agent.list_prs(state="open", limit=10)
for pr in open_prs:
    print(f"#{pr.number}: {pr.title} [{pr.state}]")

# Get specific PR
pr = agent.get_pr(42)
print(f"PR #{pr.number}: {pr.title}")
print(f"From: {pr.source_branch} → {pr.target_branch}")
print(f"Mergeable: {pr.mergeable}")

# Merge PR
agent.merge_pr(42, method="squash", delete_branch=True)

# Close PR without merging
agent.close_pr(42, comment="Not needed anymore")
```

### STATUS and DIFF Operations

```python
# Get status
status = agent.get_status()
print(status)

# Get short status
status = agent.get_status(short=True)

# Check if there are changes
if agent.has_changes():
    print("You have uncommitted changes")

# Check if clean
if agent.is_clean():
    print("Working directory is clean")

# Get diff
diff = agent.get_diff()
print(diff)

# Get staged diff
staged_diff = agent.get_diff(staged=True)

# Get diff for specific files
diff = agent.get_diff(files=["auth.py", "login.py"])

# Get list of changed files
changed = agent.get_changed_files()
print(f"Changed files: {', '.join(changed)}")

# Get staged files only
staged = agent.get_changed_files(staged=True)
```

### STASH Operations

```python
# Stash current changes
agent.stash_save("WIP: authentication feature")

# Stash with untracked files
agent.stash_save("Temp save", include_untracked=True)

# List stashes
stashes = agent.stash_list()
for stash in stashes:
    print(stash)

# Pop most recent stash
agent.stash_pop()
```

### UTILITY Operations

```python
# Get remote URL
url = agent.get_remote_url()
print(f"Remote: {url}")

# Get repository info
info = agent.get_repo_info()
print(f"Branch: {info['current_branch']}")
print(f"Remote: {info['remote_url']}")
print(f"Has changes: {info['has_changes']}")
print(f"Tracking: {info['tracking']}")
```

## Data Structures

### Branch
```python
@dataclass
class Branch:
    name: str              # Branch name
    current: bool         # Is this the current branch?
    remote: bool          # Is this a remote branch?
    tracking: str         # Upstream tracking branch
    commit: str           # Latest commit SHA
```

### Commit
```python
@dataclass
class Commit:
    sha: str              # Full commit SHA
    short_sha: str        # Short SHA (7 chars)
    message: str          # Commit message
    author: str           # Author name
    date: str             # Commit date
```

### PullRequest
```python
@dataclass
class PullRequest:
    number: int           # PR number
    title: str            # PR title
    state: str            # State (OPEN, CLOSED, MERGED)
    source_branch: str    # Source branch
    target_branch: str    # Target branch
    url: str              # PR URL
    mergeable: bool       # Can be merged?
```

## Common Workflows for Claude Code

### 1. Feature Development Workflow
```python
agent = GitWorkflowAgent()

# Create feature branch from main
agent.switch_branch("main")
agent.pull()  # Get latest
branch = agent.create_branch("user-auth", branch_type=BranchType.FEATURE)

# Make changes, then commit
agent.commit("Implemented user authentication", files=["auth.py", "models.py"])

# Push to remote
agent.push(set_upstream=True)

# Create PR
pr = agent.create_pr(
    title="Add user authentication",
    body="Implements JWT-based user authentication",
    base="main"
)
print(f"✅ Created PR: {pr.url}")
```

### 2. Bug Fix Workflow with Issue Integration
```python
agent = GitWorkflowAgent()

# Create branch for issue #5
agent.switch_branch("main")
branch = agent.create_branch("fix-issue-5", branch_type=BranchType.BUGFIX)

# Fix the bug and commit with issue reference
agent.commit_with_issue("Fixed login validation bug", issue_number=5)

# Push and create PR that closes the issue
agent.push(set_upstream=True)
pr = agent.create_pr_from_issue(issue_number=5)

print(f"✅ Created PR #{pr.number} that will close issue #5")
```

### 3. Quick Hotfix Workflow
```python
agent = GitWorkflowAgent()

# Create hotfix from main
agent.switch_branch("main")
branch = agent.create_branch("critical-fix", branch_type=BranchType.HOTFIX)

# Make urgent fix
agent.commit("Fixed critical security issue", files=["security.py"])

# Push and merge immediately
agent.push(set_upstream=True)
pr = agent.create_pr("HOTFIX: Security vulnerability", base="main")
agent.merge_pr(pr.number, method="squash")
```

### 4. Review and Cleanup Workflow
```python
agent = GitWorkflowAgent()

# Check current state
if agent.has_changes():
    print("⚠️  You have uncommitted changes")
    changed = agent.get_changed_files()
    print(f"Changed: {', '.join(changed)}")

    # Show diff
    diff = agent.get_diff()
    print(diff)

    # Decide: commit or stash
    agent.stash_save("WIP changes")

# List and clean up old branches
branches = agent.list_branches()
for branch in branches:
    if not branch.current and branch.name.startswith("old-"):
        agent.delete_branch(branch.name)
```

### 5. Multi-Branch Development
```python
agent = GitWorkflowAgent()

# Working on feature A
agent.create_branch("feature-a", branch_type=BranchType.FEATURE)
agent.commit("Part 1 of feature A")

# Need to switch to urgent task
agent.stash_save("WIP: feature A")
agent.switch_branch("main")
agent.create_branch("urgent-fix", branch_type=BranchType.BUGFIX)
agent.commit("Fixed urgent issue")
agent.push(set_upstream=True)

# Back to feature A
agent.switch_branch("feature/feature-a")
agent.stash_pop()
agent.commit("Completed feature A")
```

### 6. PR Review and Merge Flow
```python
agent = GitWorkflowAgent()

# List open PRs
prs = agent.list_prs(state="open")
for pr in prs:
    print(f"#{pr.number}: {pr.title}")

    # Check if mergeable
    pr_detail = agent.get_pr(pr.number)
    if pr_detail.mergeable:
        print(f"  ✅ Can be merged")

        # Merge with squash
        agent.merge_pr(pr.number, method="squash", delete_branch=True)
        print(f"  ✅ Merged and deleted branch")
```

## Branch Types

```python
class BranchType(Enum):
    FEATURE = "feature"   # New features
    BUGFIX = "bugfix"     # Bug fixes
    HOTFIX = "hotfix"     # Urgent fixes
    RELEASE = "release"   # Release branches
    CHORE = "chore"       # Maintenance tasks
```

## Integration with Git Issue Agent

```python
from agents.git_issue_agent import GitIssueAgent
from agents.git_workflow_agent import GitWorkflowAgent, BranchType

issue_agent = GitIssueAgent()
workflow_agent = GitWorkflowAgent()

# Create issue
issue = issue_agent.create_issue(
    title="Add user authentication",
    body="Need JWT authentication system"
)

# Create branch for issue
branch = workflow_agent.create_branch(
    f"issue-{issue.number}",
    branch_type=BranchType.FEATURE
)

# Do work, commit with reference
workflow_agent.commit_with_issue("Implemented auth", issue.number)

# Create PR and close issue
workflow_agent.push(set_upstream=True)
pr = workflow_agent.create_pr_from_issue(issue.number)

# Update issue with PR link
issue_agent.add_comment(issue.number, f"PR created: {pr.url}")
```

## Error Handling

```python
try:
    agent.create_branch("new-feature")
except RuntimeError as e:
    print(f"❌ Error: {e}")
```

Common errors:
- `Git is not installed` - Install Git
- `GitHub CLI (gh) is not installed` - Install gh CLI
- `Git command error: ...` - Check git repository state
- `GitHub CLI error: ...` - Check authentication

## Best Practices

1. **Always check status before committing**
   ```python
   if agent.has_changes():
       status = agent.get_status()
       # Review changes
   ```

2. **Use meaningful branch names with types**
   ```python
   agent.create_branch("add-auth", branch_type=BranchType.FEATURE)
   # Creates: feature/add-auth
   ```

3. **Reference issues in commits**
   ```python
   agent.commit_with_issue("Fixed bug", issue_number=42)
   ```

4. **Set upstream when pushing new branches**
   ```python
   agent.push(set_upstream=True)
   ```

5. **Use stash for context switching**
   ```python
   agent.stash_save("WIP: current feature")
   # Switch tasks
   agent.stash_pop()  # Resume work
   ```

6. **Clean up branches after merging**
   ```python
   agent.merge_pr(pr_number, delete_branch=True)
   ```

## Quick Reference

| Operation | Method | Example |
|-----------|--------|---------|
| Create branch | `create_branch()` | `agent.create_branch("feat", BranchType.FEATURE)` |
| Switch branch | `switch_branch()` | `agent.switch_branch("main")` |
| Commit | `commit()` | `agent.commit("message")` |
| Push | `push()` | `agent.push(set_upstream=True)` |
| Create PR | `create_pr()` | `agent.create_pr("title")` |
| Status | `get_status()` | `agent.get_status()` |
| Diff | `get_diff()` | `agent.get_diff(staged=True)` |
| Stash | `stash_save()` | `agent.stash_save("message")` |

## Prerequisites

- Git installed: `brew install git`
- GitHub CLI installed: `brew install gh`
- Authenticated: `gh auth login`
