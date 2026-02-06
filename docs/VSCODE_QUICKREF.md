# Ten8t VSCode Quick Reference

## 🚀 Getting Started
```bash
git clone https://github.com/hucker/ten8t.git
cd ten8t
code .
# Install recommended extensions when prompted
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## 🤖 GitHub Copilot Shortcuts

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| **Inline Chat** | `Ctrl+I` | `Cmd+I` |
| **Chat Panel** | `Ctrl+Alt+I` | `Cmd+Alt+I` |
| **Quick Chat** | `Ctrl+Shift+I` | `Cmd+Shift+I` |

### Useful Copilot Commands
- `/explain` - Explain selected code
- `/fix` - Suggest fixes for problems
- `/tests` - Generate tests
- `@workspace` - Ask about the entire codebase
- `#file` - Reference a specific file
- `#selection` - Reference selected code

### Example Questions for Ten8t
```
@workspace How does the Ten8t checker system work?
Create a Ten8t check function for file validation
/explain this Ten8t result object
/tests Generate pytest tests for this check function
Show me how to use Ten8t with FastAPI
```

## ⌨️ VSCode Shortcuts

### Navigation
| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Quick Open File | `Ctrl+P` | `Cmd+P` |
| Go to Symbol | `Ctrl+Shift+O` | `Cmd+Shift+O` |
| Go to Definition | `F12` | `F12` |
| Find References | `Shift+F12` | `Shift+F12` |
| Search in Files | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| Command Palette | `Ctrl+Shift+P` | `Cmd+Shift+P` |

### Editing
| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Format Document | `Shift+Alt+F` | `Shift+Option+F` |
| Quick Fix | `Ctrl+.` | `Cmd+.` |
| Rename Symbol | `F2` | `F2` |
| Multi-cursor | `Ctrl+Alt+↓/↑` | `Cmd+Option+↓/↑` |

### Debugging
| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Start/Continue | `F5` | `F5` |
| Step Over | `F10` | `F10` |
| Step Into | `F11` | `F11` |
| Step Out | `Shift+F11` | `Shift+F11` |
| Toggle Breakpoint | `F9` | `F9` |
| Stop Debugging | `Shift+F5` | `Shift+F5` |

### Testing
| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Run Test | Click icon in gutter | Click icon in gutter |
| Debug Test | Right-click → Debug | Right-click → Debug |
| Show Testing Panel | `Ctrl+Shift+P` → "Test" | `Cmd+Shift+P` → "Test" |

## 🎯 Ten8t-Specific Tasks

Press `Ctrl+Shift+P` → "Tasks: Run Task" → Select:

### Running Checks
- **Ten8t: Run Checks (Examples)** - Run all example checks
- **Ten8t: Run Current File** - Run Ten8t on current file

### Testing
- **Pytest: Run All Tests** - Run entire test suite
- **Pytest: Run Current Test File** - Run tests in current file
- **Pytest: Run with Coverage** - Run with coverage report

### Code Quality
- **Lint: Run Pylint** - Check code with pylint
- **Lint: Run Ruff** - Fast linting with ruff
- **Format: Run Ruff Format** - Format code
- **Type Check: Run MyPy** - Type checking

### Demos
- **Ten8t: Start API Server** - Launch FastAPI server
- **Ten8t: Run Streamlit Demo** - Launch Streamlit UI

## 🐛 Debug Configurations

Press `F5` and select:

1. **Python: Ten8t CLI (Module)** - Debug Ten8t on examples
2. **Python: Ten8t CLI with Typer (Module)** - Debug CLI with module
3. **Python: Ten8t CLI with Typer (Package)** - Debug CLI with package
4. **Python: Ten8t API Server** - Debug FastAPI server
5. **Python: Current File** - Debug current file
6. **Python: Pytest (Current File)** - Debug current test file
7. **Python: Pytest (All Tests)** - Debug all tests

## 📝 Common Workflows

### Create a New Ten8t Check
1. Ask Copilot: `Create a Ten8t check function for [your use case]`
2. Review and refine the generated code
3. Press `F5` to debug and test it
4. Ask Copilot: `/tests Generate pytest tests for this`

### Debug a Failing Check
1. Set breakpoint in your check function (click left of line number)
2. Press `F5` → Select "Python: Ten8t CLI (Module)"
3. Inspect variables in Debug panel
4. Ask Copilot: `Why is this check failing?`

### Run and Test Your Changes
1. Make your changes
2. Auto-format on save (already configured)
3. Run task: "Pytest: Run All Tests"
4. Run task: "Lint: Run Ruff"
5. Commit changes

### Explore the Codebase
1. Press `Ctrl+P` to quickly open files
2. Use `F12` to jump to definitions
3. Ask Copilot: `@workspace Where is [feature] implemented?`
4. Use `Shift+F12` to find all references

## 🎓 Learning Resources

- **Full Setup Guide:** [docs/VSCODE_SETUP.md](VSCODE_SETUP.md)
- **Ten8t Documentation:** https://ten8t.readthedocs.io/
- **VSCode Python Guide:** https://code.visualstudio.com/docs/python/python-tutorial
- **GitHub Copilot Docs:** https://docs.github.com/en/copilot

## 💡 Pro Tips

1. **Use `@workspace` prefix** when asking Copilot about Ten8t-specific code
2. **Select code before asking** for more context-aware responses
3. **Iterate on Copilot responses** - ask follow-up questions to refine
4. **Pin frequently used files** - Right-click tab → Pin
5. **Split editor** for side-by-side comparison (`Ctrl+\`)
6. **Keep terminal open** at bottom for quick command access
7. **Use Testing panel** for visual test running and debugging

## 🆘 Troubleshooting

**Import errors?**
- Check Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter" → Choose `.venv`
- Verify PYTHONPATH in `.vscode/settings.json`

**Tests not discovered?**
- Check Testing panel is using pytest
- Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

**Copilot not responding?**
- Check Copilot icon in status bar (bottom-right)
- Sign in to GitHub if needed
- Verify subscription at https://github.com/settings/copilot

**Tasks failing?**
- Activate virtual environment in terminal
- Install dependencies: `pip install -e .`
- Check error message and ask Copilot for help!

---

**Need help?** Press `Ctrl+Alt+I` and ask: `@workspace How do I [your question]?`
