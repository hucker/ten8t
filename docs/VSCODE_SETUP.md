# Visual Studio Code Setup for Ten8t Development

This guide helps you set up Visual Studio Code for local Ten8t development, including how to use AI coding assistants like GitHub Copilot.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/hucker/ten8t.git
   cd ten8t
   ```

2. **Open in VSCode**
   ```bash
   code .
   ```

3. **Install recommended extensions** (VSCode will prompt you, or see [Recommended Extensions](#recommended-extensions))

4. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate it
   # On Linux/Mac:
   source .venv/bin/activate
   # On Windows:
   .venv\Scripts\activate
   
   # Install dependencies
   pip install -e .
   pip install -r requirements.txt
   ```

5. **Select Python interpreter** in VSCode (Ctrl+Shift+P → "Python: Select Interpreter" → choose `.venv`)

## VSCode Configuration Files

The repository includes pre-configured VSCode files in the `.vscode/` directory:

### `.vscode/launch.json` - Debug Configurations

Launch configurations for debugging Ten8t:

- **Python: Ten8t CLI (Module)** - Run Ten8t checks on the examples folder
- **Python: Ten8t CLI with Typer (Module)** - Run Ten8t CLI with module path
- **Python: Ten8t CLI with Typer (Package)** - Run Ten8t CLI with package path
- **Python: Ten8t API Server** - Start the FastAPI server
- **Python: Current File** - Debug the currently open Python file
- **Python: Pytest (Current File)** - Debug tests in current file
- **Python: Pytest (All Tests)** - Debug all tests

**Usage:** Press `F5` or go to Run → Start Debugging, then select a configuration.

### `.vscode/tasks.json` - Task Definitions

Pre-configured tasks for common operations:

| Task | Description | Shortcut |
|------|-------------|----------|
| **Ten8t: Run Checks (Examples)** | Run Ten8t on example checks | Terminal → Run Task |
| **Ten8t: Run Current File** | Run Ten8t on currently open file | Terminal → Run Task |
| **Pytest: Run All Tests** | Run entire test suite | Ctrl+Shift+P → "Test" |
| **Pytest: Run Current Test File** | Run tests in current file | Terminal → Run Task |
| **Pytest: Run with Coverage** | Run tests with coverage report | Terminal → Run Task |
| **Lint: Run Pylint** | Run pylint on source code | Terminal → Run Task |
| **Lint: Run Ruff** | Run ruff linter | Terminal → Run Task |
| **Format: Run Ruff Format** | Format code with ruff | Terminal → Run Task |
| **Type Check: Run MyPy** | Run type checking | Terminal → Run Task |
| **Build: Install Package** | Install Ten8t in development mode | Terminal → Run Task |
| **Ten8t: Start API Server** | Start FastAPI server (background) | Terminal → Run Task |
| **Ten8t: Run Streamlit Demo** | Launch Streamlit demo | Terminal → Run Task |

**Usage:** Press `Ctrl+Shift+P` → "Tasks: Run Task" → Select task, or use `Ctrl+Shift+B` for default build task.

### `.vscode/settings.json` - Workspace Settings

Configured settings include:
- Python testing with pytest
- Code formatting with Ruff
- Auto-formatting on save
- Python path configuration
- File exclusions for cleaner workspace
- Spell checking with custom dictionary

### `.vscode/extensions.json` - Recommended Extensions

VSCode will prompt you to install these when you open the project.

## Recommended Extensions

### Essential for Python Development
1. **Python** (`ms-python.python`) - Core Python support
2. **Pylance** (`ms-python.vscode-pylance`) - Fast Python language server
3. **Python Debugger** (`ms-python.debugpy`) - Debugging support
4. **Ruff** (`charliermarsh.ruff`) - Fast Python linter and formatter

### Essential for Ten8t Development
5. **Even Better TOML** (`tamasfe.even-better-toml`) - TOML file support (for pyproject.toml)
6. **YAML** (`redhat.vscode-yaml`) - YAML file support

### Recommended for Better Experience
7. **Code Spell Checker** (`streetsidesoftware.code-spell-checker`) - Catch typos
8. **GitHub Pull Requests** (`github.vscode-pull-request-github`) - PR management
9. **GitLens** (`eamodio.gitlens`) - Enhanced Git integration

### AI Coding Assistants (Highly Recommended!)
- **GitHub Copilot** (`GitHub.copilot`) - AI pair programmer
- **GitHub Copilot Chat** (`GitHub.copilot-chat`) - AI chat assistant in VSCode

## Using AI Coding Assistants in VSCode

### GitHub Copilot Setup

1. **Install GitHub Copilot extensions:**
   - GitHub Copilot (`GitHub.copilot`)
   - GitHub Copilot Chat (`GitHub.copilot-chat`)

2. **Sign in to GitHub** (if prompted)

3. **Verify Copilot is active** - Look for the Copilot icon in the status bar

### How to Ask Questions in VSCode with Copilot Chat

#### Method 1: Inline Chat (Ctrl+I)
- Press `Ctrl+I` (or `Cmd+I` on Mac) while editing
- Ask questions directly in your code
- Example: "How do I create a Ten8t checker function?"

#### Method 2: Chat Panel (Ctrl+Alt+I)
- Press `Ctrl+Alt+I` (or `Cmd+Alt+I` on Mac)
- Opens a dedicated chat panel on the side
- Better for longer conversations and explanations

#### Method 3: Quick Chat (Ctrl+Shift+I)
- Press `Ctrl+Shift+I` (or `Cmd+Shift+I` on Mac)
- Quick overlay chat window
- Great for quick questions

### Effective Questions for Ten8t Development

Here are examples of questions you can ask Copilot Chat about Ten8t:

#### Understanding the Codebase
```
@workspace How does the Ten8t checker system work?
@workspace Where are the rule checking functions defined?
@workspace Explain how the Ten8t result system works
```

#### Creating New Checks
```
Create a Ten8t check function that validates if a file exists
How do I add custom attributes to a Ten8t check?
Show me an example of a Ten8t check with retry logic
```

#### Debugging
```
Why is my Ten8t check function failing?
How do I debug a Ten8t checker in VSCode?
Explain this error message: [paste error]
```

#### Testing
```
How do I write a test for a Ten8t check function?
Create a pytest test for my check_file_exists function
How do I run specific tests in this project?
```

#### Integration
```
How do I integrate Ten8t with a FastAPI application?
Show me how to use Ten8t results in Streamlit
How do I run Ten8t checks from a Python script?
```

### Using Copilot Chat Features

#### Slash Commands
- `/explain` - Explain selected code
- `/fix` - Suggest fixes for problems
- `/tests` - Generate tests
- `/help` - Get help on Copilot features

#### Context Participants
- `@workspace` - Ask about the entire workspace
- `@vscode` - Ask about VSCode features
- `@terminal` - Ask about terminal commands
- `#file` - Reference specific files
- `#selection` - Reference selected code

#### Example Workflow
```
1. Select a function in your code
2. Press Ctrl+I
3. Type: "/explain this function"
4. Or: "Add error handling to this function"
5. Or: "/tests Generate pytest tests for this"
```

## Common Development Tasks

### Running Ten8t Checks

**Using the Command Line:**
```bash
# Run on a specific file
python -m ten8t path/to/check_file.py

# Run on a package directory
python -m ten8t path/to/check_package/

# Run on examples
python -m ten8t src/ten8t/examples
```

**Using VSCode:**
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Tasks: Run Task"
3. Select "Ten8t: Run Checks (Examples)"

**Using Debug Mode:**
1. Press `F5`
2. Select "Python: Ten8t CLI (Module)"
3. Set breakpoints as needed

### Running Tests

**Using the Testing Panel:**
1. Click the Testing icon in the Activity Bar (left side)
2. Click "Run Tests" or run individual tests
3. View results inline

**Using Tasks:**
1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select "Pytest: Run All Tests"

**Using Command Line:**
```bash
# Run all tests
pytest test/ -v

# Run specific test file
pytest test/test_checker.py -v

# Run with coverage
pytest --cov=src/ten8t --cov-report=html test/
```

### Code Formatting and Linting

**Auto-format on Save:** Already configured! Just save your file (`Ctrl+S`)

**Manual Format:**
1. Right-click in editor → "Format Document"
2. Or `Shift+Alt+F`

**Run Linting:**
1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select "Lint: Run Ruff" or "Lint: Run Pylint"

### Debugging

**Set Breakpoints:**
- Click in the gutter (left of line numbers) to add/remove breakpoints
- Red dot appears when breakpoint is set

**Start Debugging:**
1. Press `F5` or click Run → Start Debugging
2. Choose a debug configuration
3. Use debug controls:
   - `F5` - Continue
   - `F10` - Step Over
   - `F11` - Step Into
   - `Shift+F11` - Step Out
   - `Shift+F5` - Stop

**Debug Console:**
- Available during debug sessions
- Evaluate expressions, inspect variables

### Working with Git

**Built-in Git:**
- View changes in Source Control panel (`Ctrl+Shift+G`)
- Stage changes, commit, push/pull

**With GitLens:**
- Inline blame annotations
- File/line history
- Rich commit search

## Troubleshooting

### Python Interpreter Not Found
1. `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Choose your `.venv` interpreter
3. If not listed, create virtual environment first

### Import Errors in Code
1. Ensure `PYTHONPATH` includes `src/` directory
2. Check `.vscode/settings.json` has correct `python.analysis.extraPaths`
3. Restart VSCode window

### Tests Not Discovered
1. Check Testing panel shows pytest
2. Verify `python.testing.pytestEnabled` is true in settings
3. Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Copilot Not Working
1. Check Copilot icon in status bar (bottom right)
2. Sign in to GitHub if needed
3. Verify subscription at https://github.com/settings/copilot
4. Check extension is installed and enabled

### Tasks Not Running
1. Ensure dependencies are installed (`pip install -e .`)
2. Check terminal has activated virtual environment
3. Try running command manually first to diagnose

## Tips and Best Practices

### Workspace Organization
- Keep terminal panel open at bottom for quick access
- Use split editor for side-by-side code comparison
- Pin frequently used files

### Keyboard Shortcuts
- `Ctrl+P` - Quick open file
- `Ctrl+Shift+F` - Search across files
- `F12` - Go to definition
- `Shift+F12` - Find all references
- `Ctrl+.` - Quick fix
- `F2` - Rename symbol

### Working with Copilot
- Be specific in your questions
- Provide context about what you're trying to do
- Use `@workspace` to query entire codebase
- Review suggestions before accepting
- Iterate on responses if needed

### Development Workflow
1. Create/checkout feature branch
2. Make changes with Copilot assistance
3. Run tests frequently (`Ctrl+Shift+P` → Run Task → Pytest)
4. Format and lint before committing
5. Use debug mode to troubleshoot issues
6. Ask Copilot for help when stuck!

## Additional Resources

- [Ten8t Documentation](https://ten8t.readthedocs.io/)
- [VSCode Python Documentation](https://code.visualstudio.com/docs/python/python-tutorial)
- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [Ten8t Repository](https://github.com/hucker/ten8t)

## Getting Help

### In VSCode with Copilot
- Press `Ctrl+Alt+I` and ask your question
- Use `@workspace` for project-specific questions
- Use `/help` to learn about Copilot features

### Community
- GitHub Issues: https://github.com/hucker/ten8t/issues
- GitHub Discussions: https://github.com/hucker/ten8t/discussions

### Example Questions to Ask Copilot
```
@workspace How do I create a new Ten8t check for API endpoints?
@workspace What's the best way to test my Ten8t rules?
@workspace Show me examples of Ten8t integration with FastAPI
/explain #selection (select code first)
/tests Create pytest tests for this function
```

---

**Ready to start?** Open the repository in VSCode, install the recommended extensions, and press `Ctrl+Alt+I` to start chatting with Copilot!
