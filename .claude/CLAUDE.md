# Project-Specific Claude Code Instructions

## 🐍 Python Environment

**Python Version**: Python 3.11
**Environment**: Virtual environment with `requirements.txt`

### Setup
- This project uses Python 3.11 on the user's laptop
- Dependencies are managed via `requirements.txt`
- Always use the virtual environment for Python operations
- When adding new dependencies, update `requirements.txt`

### Running Python Code
- Use `python3` or `python` (whichever points to 3.11 in the venv)
- Check compatibility with Python 3.11 when suggesting libraries
- Test scripts should be compatible with Python 3.11

## 🤖 Git Workflow Tools: Two Options

This project has **two ways** to work with Git and GitHub. Choose based on the task type:

### Option 1: Interactive Agents (Primary - Use During Claude Code Sessions)

**CRITICAL**: For interactive development, you MUST use these agents instead of raw git/gh commands.

### Required Agent Usage

**For ANY GitHub issue operations**, use `GitIssueAgent`:
- ✅ Creating, reading, updating, deleting issues
- ✅ Listing issues, searching issues
- ✅ Adding comments, managing labels
- ❌ DO NOT use `gh issue` commands directly
- ❌ DO NOT use Bash for issue operations

**For ANY Git/PR operations**, use `GitWorkflowAgent`:
- ✅ Creating branches, switching branches
- ✅ Committing changes, pushing code
- ✅ Creating PRs, listing PRs
- ✅ Checking status, viewing diffs
- ❌ DO NOT use raw `git` commands directly (except for read-only operations)
- ❌ DO NOT use `gh pr` commands directly

### Agent Import Pattern (Use This Every Time)
```python
from agents.git_issue_agent import GitIssueAgent, IssueState
from agents.git_workflow_agent import GitWorkflowAgent, BranchType

# Initialize agents
issue_agent = GitIssueAgent()
workflow_agent = GitWorkflowAgent()

# Now use them for all operations
```

### When to Use Each Agent

| Task | Use This Agent | Example |
|------|----------------|---------|
| List issues | GitIssueAgent | `issue_agent.list_issues()` |
| Create issue | GitIssueAgent | `issue_agent.create_issue("title")` |
| Create branch | GitWorkflowAgent | `workflow_agent.create_branch("name")` |
| Commit changes | GitWorkflowAgent | `workflow_agent.commit("message")` |
| Push code | GitWorkflowAgent | `workflow_agent.push(set_upstream=True)` |
| Create PR | GitWorkflowAgent | `workflow_agent.create_pr("title")` |
| Check status | GitWorkflowAgent | `workflow_agent.get_status()` |

### Available Agents

1. **GitIssueAgent** (`agents/git_issue_agent.py`)
   - Complete CRUD operations for GitHub issues
   - Search, filter, and manage issues programmatically
   - Full documentation: `agents/GIT_ISSUE_AGENT_GUIDE.md`

2. **GitWorkflowAgent** (`agents/git_workflow_agent.py`)
   - Branch management with type prefixes (feature/, bugfix/, hotfix/)
   - Smart commits with issue references
   - PR creation and management
   - Status, diff, stash operations
   - Full documentation: `agents/GIT_WORKFLOW_AGENT_GUIDE.md`

### Option 2: GitHub Actions (For Automated Tasks)

**Use for**: One-shot automated tasks that don't need incremental commits

**Setup**: `.github/workflows/claude.yml` (configured)

**Usage**: Comment on issues or PRs with `@claude` mentions
```
@claude write comprehensive tests for the RDS connection
@claude /review this PR
@claude fix the bug described in this issue
@claude generate API documentation
```

**What happens**:
- Claude reads the issue/PR context
- Analyzes codebase
- Creates complete PR with all changes
- You review and merge

### When to Use Each:

| Task | Use This | Why |
|------|----------|-----|
| Building features step-by-step | **Interactive Agents** | Need feedback and incremental commits |
| Writing all tests for a module | **GitHub Actions** | Just want complete test PR to review |
| Debugging with feedback | **Interactive Agents** | Back-and-forth problem solving |
| Code review automation | **GitHub Actions** | Async review, no interaction needed |
| Implementing with approval | **Interactive Agents** | Approve each change as you go |
| Generate documentation | **GitHub Actions** | One-shot generation, review result |

**Note**: GitHub Actions requires:
1. Installing the Claude GitHub App: https://github.com/apps/claude
2. Adding `ANTHROPIC_API_KEY` to repository secrets

## Git Workflow Rules

### Issue-Focused Development
**CRITICAL**: Work ONLY on what's in the current issue. Never work ahead or combine multiple issues.

- ✅ Complete ONE issue at a time
- ✅ Work only on tasks listed in the issue
- ✅ Commit and create PR for current issue before moving to next
- ❌ DO NOT work on multiple issues in one branch
- ❌ DO NOT add extra features not in the issue
- ❌ DO NOT start next issue before current one has a PR

**Pattern**:
1. Work on Issue #5 → Commit → PR → STOP
2. User reviews and merges PR
3. Only then start Issue #6

### Pull Request Approval
**IMPORTANT**: Never automatically merge PRs. Always let the user approve and merge PRs manually.

- ✅ Create PRs using `workflow_agent.create_pr()`
- ✅ Provide PR links and details to the user
- ❌ DO NOT call `merge_pr()` or `gh pr merge` without explicit user instruction
- ❌ DO NOT auto-approve or auto-merge PRs

### Commit Strategy
**IMPORTANT**: Make commits during the session after positive user feedback, not just at the end.

- ✅ Commit after completing a logical piece of work
- ✅ Commit when user gives positive feedback or approval
- ✅ Make incremental commits throughout the session
- ✅ Include progress summary in commit messages
- ❌ DO NOT wait until end of session to commit everything
- ❌ DO NOT make giant commits with unrelated changes

**When to commit**:
- User says "looks good", "great", "perfect", "yes", "approved"
- Completed a checklist item from the issue
- Finished a logical unit of work (function, feature, fix)
- Before switching context or taking a break

**PR descriptions**:
- Keep concise - user can see file changes in GitHub
- Brief summary of what was done (2-3 sentences)
- Overall progress: "Completed X of Y tasks"
- What remains (if any)
- Reference issue number
- ❌ DO NOT write long detailed descriptions
- ❌ DO NOT list every file changed (GitHub shows this)

**Commit messages**:
- Keep short and descriptive
- Focus on "what" and "why", not "how"
- Example: "Added EC2 setup guide for SSH tunnel" not "Created new markdown file in docs folder with detailed instructions about..."
- ❌ DO NOT write lengthy commit messages

### Standard Workflow Pattern
1. Create issue: `issue = issue_agent.create_issue("Fix bug", project="Data Analysis Agent POC - Retail")`
2. Create branch: `workflow_agent.create_branch(f"issue-{issue.number}", BranchType.BUGFIX)`
3. Make changes and commit: `workflow_agent.commit_with_issue("Fixed", issue.number)`
4. Push: `workflow_agent.push(set_upstream=True)`
5. Create PR: `pr = workflow_agent.create_pr_from_issue(issue.number)`
6. **STOP** - User reviews and merges manually

### GitHub Project Management
**IMPORTANT**: All new issues MUST be added to the GitHub Project.

- ✅ **Project Name**: "Data Analysis Agent POC - Retail"
- ✅ When creating issues, always include: `project="Data Analysis Agent POC - Retail"`
- ✅ This keeps all work organized in one project board
- ✅ User can track progress across all issues

Example:
```python
# Always include project parameter
issue = issue_agent.create_issue(
    title="Add authentication",
    body="Implement JWT auth",
    project="Data Analysis Agent POC - Retail"
)
```

## File Management Rules

### README.md Protection
**CRITICAL**: NEVER modify `/README.md` in the root folder.

- ❌ DO NOT edit, update, or change README.md
- ❌ DO NOT add sections or content to README.md
- ✅ README.md is reserved for user's personal notes and comments only
- ✅ Create all documentation in `docs/` folder instead

### Claude-Generated Content Location
**CRITICAL**: All Claude-generated content must go in the `.claude/` folder with proper organization.

- ✅ Documentation & guides → `.claude/docs/`
- ✅ Test scripts → `.claude/tests/`
- ✅ Demo scripts → `.claude/demos/`
- ✅ Utility scripts → `.claude/utilities/`
- ❌ DO NOT scatter files in root or random locations
- ❌ NEVER put documentation in root README.md

### Folder Organization
```
.claude/
  ├── CLAUDE.md                # Project-specific instructions
  ├── settings.local.json      # Claude Code settings
  ├── docs/                    # All documentation and guides
  ├── tests/                   # Test scripts for validation
  ├── demos/                   # Demo and example scripts
  └── utilities/               # Utility and helper scripts
agents/                        # Git automation agents
datasets/                      # Data files
README.md                      # User's personal notes ONLY
```

**Benefits**:
- All Claude content organized in ONE place under .claude/
- Clear separation by purpose (docs, tests, demos, utilities)
- Easy to find, review, or clean up
- Natural grouping with Claude configuration

## Cleanup Rules

### Temporary Files
Always clean up temporary scripts and files after completing tasks:
- Remove test scripts (test_*.py, show_*.py, etc.)
- Remove temporary debugging files
- Keep workspace clean for the user

### Git Branches
- Create feature branches for all work
- Never work directly on main/master
- Switch back to main after creating PR
