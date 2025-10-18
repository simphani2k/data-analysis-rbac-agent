# GitHub Actions Setup Guide

This guide will help you set up Claude Code GitHub Actions for automated tasks.

## What is GitHub Actions Integration?

GitHub Actions allows Claude to respond to `@claude` mentions in issues and PRs, creating automated PRs for tasks like:
- Writing tests
- Code reviews
- Bug fixes
- Documentation generation

## Prerequisites

- Repository admin access
- Anthropic API key (from console.anthropic.com)

## Setup Steps

### Step 1: Install the Claude GitHub App

1. Go to: https://github.com/apps/claude
2. Click "Install"
3. Select your repository: `simphani2k/data-analysis-rbac-agent`
4. Grant permissions:
   - ✅ Contents (Read & Write)
   - ✅ Issues (Read & Write)
   - ✅ Pull Requests (Read & Write)

### Step 2: Add API Key to Repository Secrets

1. Go to your repository on GitHub
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: Your API key from console.anthropic.com
6. Click **Add secret**

### Step 3: Verify Workflow File

The workflow file is already created at `.github/workflows/claude.yml`:

```yaml
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

This workflow triggers when:
- Someone comments on an issue
- Someone comments on a PR review

## How to Use

### In Issues

Comment with `@claude` followed by your request:

```
@claude write comprehensive integration tests for the RDS connection module
```

Claude will:
1. Analyze the codebase
2. Write all the tests
3. Create a PR with the tests
4. You review and merge

### In Pull Requests

Request reviews or fixes:

```
@claude /review
```

Or:

```
@claude fix the type errors in this PR
```

## Example Use Cases

### 1. Test Generation
```
Issue #5: Test RDS database connection
Comment: @claude write unit and integration tests for all functions in test_rds_connection.py
Result: PR with comprehensive test suite
```

### 2. Documentation
```
Comment: @claude generate API documentation for all endpoints in the agents module
Result: PR with complete API docs
```

### 3. Code Review
```
PR #6: Add authentication
Comment: @claude /review
Result: Claude reviews code and suggests improvements
```

### 4. Bug Fixes
```
Issue #7: TypeError in dashboard
Comment: @claude analyze and fix the TypeError described in this issue
Result: PR with bug fix
```

## When to Use vs Interactive Agents

| Scenario | Use GitHub Actions | Use Interactive Agents |
|----------|-------------------|------------------------|
| "Write all tests for module X" | ✅ Yes - one PR | ❌ Too automated |
| "Build auth system step by step" | ❌ Too automated | ✅ Yes - with feedback |
| "Review this PR" | ✅ Yes - automated review | ❌ Not applicable |
| "Fix bug and let me approve each step" | ❌ No feedback loop | ✅ Yes - incremental |
| "Generate docs for entire API" | ✅ Yes - one shot | ❌ Too much at once |

## Cost Considerations

- GitHub Actions minutes (usually free for public repos)
- Claude API token usage (varies by task complexity)
- Monitor usage at console.anthropic.com

## Troubleshooting

### Claude doesn't respond to @claude mentions

1. Check if GitHub App is installed: https://github.com/settings/installations
2. Verify `ANTHROPIC_API_KEY` secret exists in repository settings
3. Check workflow file is in `.github/workflows/claude.yml`
4. View Actions tab in GitHub to see if workflow ran

### API Key Issues

- Get your key from: https://console.anthropic.com/settings/keys
- Make sure it's added as `ANTHROPIC_API_KEY` (exact name)
- Key should start with `sk-ant-`

## Testing Your Setup

1. Create a test issue or use an existing one
2. Comment: `@claude say hello`
3. Check the Actions tab to see if the workflow triggered
4. Claude should respond to your comment

## Support

- Claude Code Docs: https://docs.claude.com/en/docs/claude-code/github-actions
- GitHub Issues: For problems with this setup

---

**Note**: This is complementary to the interactive agents in `agents/`. Use GitHub Actions for one-shot automated tasks, and interactive agents for development with feedback.
