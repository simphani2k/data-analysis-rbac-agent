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


## File Management Rules

### README.md Protection
**CRITICAL**: NEVER modify `/README.md` in the root folder.

- ❌ DO NOT edit, update, or change README.md
- ❌ DO NOT add sections or content to README.md
- ✅ README.md is reserved for user's personal notes and comments only
- ✅ Create all documentation in `docs/` folder instead

### Claude-Generated Content Location
**CRITICAL**: Always check existing folder structure FIRST before creating files.

**Primary Locations (Check These First)**:
- ✅ Documentation & guides → `docs/` (root folder)
- ✅ Test scripts → `scripts/tests/`
- ✅ Demo scripts → `scripts/demos/`
- ✅ Utility scripts → `scripts/utilities/`

**Rules**:
- ❌ DO NOT scatter files in root or random locations
- ❌ NEVER put documentation in root README.md
- ✅ ALWAYS check if `docs/` or `scripts/` folders exist before creating files
- ✅ Use existing project structure when available

### Folder Organization
```
docs/                          # Documentation and guides (primary)
scripts/
  ├── tests/                   # Test scripts for validation
  ├── demos/                   # Demo and example scripts
  └── utilities/               # Utility and helper scripts
.claude/
  ├── CLAUDE.md                # Project-specific instructions
  ├── settings.local.json      # Claude Code settings
  ├── docs/                    # Fallback for documentation
  ├── tests/                   # Fallback for test scripts
  ├── demos/                   # Fallback for demo scripts
  └── utilities/               # Fallback for utility scripts
agents/                        # Git automation agents
datasets/                      # Data files
README.md                      # User's personal notes ONLY
```

**Benefits**:
- Respects existing project structure
- Keeps documentation accessible in root `docs/`
- Scripts organized under `scripts/` by type
- Clear separation by purpose

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
