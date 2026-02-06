# Getting Started with Ten8t in VSCode

> **TL;DR**: Clone repo → Open in VSCode → Install extensions → Create venv → Ask Copilot questions!

## Quick Start (5 minutes)

```bash
# 1. Clone and open
git clone https://github.com/hucker/ten8t.git
cd ten8t
code .

# 2. When VSCode opens, click "Install" when prompted for extensions

# 3. Create Python environment (in VSCode terminal: Ctrl+`)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .

# 4. Select Python interpreter
# Press Ctrl+Shift+P → "Python: Select Interpreter" → Choose .venv

# 5. Test it works
# Press F5 → Select "Python: Ten8t CLI (Module)"
```

**Done!** Now you can:
- Press `Ctrl+Alt+I` to chat with GitHub Copilot
- Press `F5` to debug Ten8t checks
- Use `Ctrl+Shift+P` → "Tasks: Run Task" for common operations

## What You Get with This Setup

### ✅ Instant Debugging
- Set breakpoints by clicking left of line numbers
- Press `F5` to start debugging
- Inspect variables, step through code, evaluate expressions

### ✅ AI Assistant (GitHub Copilot)
- Press `Ctrl+I` for inline chat
- Press `Ctrl+Alt+I` for full chat panel
- Ask questions like:
  - `@workspace How do I create a Ten8t check?`
  - `Create a Ten8t check for API validation`
  - `/explain` (with code selected)
  - `/tests` (to generate tests)

### ✅ Automated Testing
- Click Testing icon in Activity Bar
- Run/debug individual tests
- See results inline in your code

### ✅ One-Click Tasks
Press `Ctrl+Shift+P` → "Tasks: Run Task":
- Run Ten8t checks
- Run pytest
- Lint code
- Format code
- Start API server
- Launch Streamlit demo

### ✅ Smart Code Completion
- Auto-complete as you type
- Jump to definitions with `F12`
- Find references with `Shift+F12`
- Automatic imports organization

### ✅ Auto-Formatting
- Saves automatically format your code
- Ruff handles formatting and linting
- No need to manually run formatters

## First Steps After Setup

### 1. Explore the Examples
```bash
# Open the examples directory
Ctrl+P → type "examples"
```
Browse through example check functions to understand the patterns.

### 2. Ask Copilot About the Codebase
Press `Ctrl+Alt+I` and try these questions:
```
@workspace What is Ten8t and how does it work?
@workspace Show me examples of Ten8t check functions
@workspace How do I create my first check?
```

### 3. Run Example Checks
Press `F5` and select "Python: Ten8t CLI (Module)" to run the examples.

### 4. Try the Interactive Demos
`Ctrl+Shift+P` → "Tasks: Run Task":
- "Ten8t: Start API Server" - Opens FastAPI at http://localhost:8000
- "Ten8t: Run Streamlit Demo" - Opens Streamlit UI

### 5. Create Your First Check
1. Create a new file in `src/ten8t/examples/`
2. Press `Ctrl+I` and ask: `Create a Ten8t check for [your use case]`
3. Press `F5` to test it
4. Ask Copilot: `/tests Generate pytest tests for this`

## How to Ask Questions in VSCode

This is what you wanted to know! Here's how:

### Method 1: Inline Chat (Ctrl+I)
**Best for**: Quick questions while editing code
```
1. Press Ctrl+I (or Cmd+I on Mac)
2. Type your question
3. Get inline suggestions
```

**Example**:
- While editing: `Ctrl+I` → "Add error handling to this function"
- On empty line: `Ctrl+I` → "Create a Ten8t check for database"

### Method 2: Chat Panel (Ctrl+Alt+I)
**Best for**: Longer conversations and exploration
```
1. Press Ctrl+Alt+I (or Cmd+Alt+I on Mac)
2. Opens a dedicated chat panel on the side
3. Have a back-and-forth conversation
```

**Example questions**:
```
@workspace How does the Ten8t checker system work?
@workspace Where are the check functions defined?
Show me examples of using the categories decorator
Create a Ten8t check that validates API response times
```

### Method 3: Quick Chat (Ctrl+Shift+I)
**Best for**: Quick overlay without opening full panel
```
1. Press Ctrl+Shift+I
2. Quick popup appears
3. Type question and get answer
```

### Method 4: Selected Code Actions
**Best for**: Working with existing code
```
1. Select some code
2. Press Ctrl+I
3. Use slash commands:
   - /explain - Explain this code
   - /fix - Fix problems
   - /tests - Generate tests
   - /docs - Generate documentation
```

## Power User Tips

### Use @workspace for Project Context
Always use `@workspace` when asking about Ten8t:
```
❌ How do I create a check function?
✅ @workspace How do I create a check function?
```
The second version knows about the Ten8t codebase!

### Reference Specific Files
```
@workspace #file:src/ten8t/ten8t_checker.py Explain the run_all method
```

### Chain Your Questions
```
1. Create a Ten8t check for API health
2. (after reviewing) Add retry logic with 3 attempts
3. (after reviewing) Add better error messages
4. /tests Generate comprehensive tests for this
```

### Learn from Examples
```
@workspace Show me examples of Ten8t checks that use categories
@workspace Find checks that use the attempt decorator
@workspace What's in the examples directory?
```

## Common Questions and Answers

### "How do I run Ten8t checks?"
```
Option 1: Press F5 → "Python: Ten8t CLI (Module)"
Option 2: Ctrl+Shift+P → Tasks → "Ten8t: Run Checks"
Option 3: Terminal → python -m ten8t src/ten8t/examples
```

### "How do I debug a check function?"
```
1. Open the file with your check
2. Click left of line number to set breakpoint (red dot appears)
3. Press F5 → Choose debug configuration
4. When it stops, inspect variables in left panel
5. Use F10 to step through line by line
```

### "How do I run tests?"
```
Option 1: Click Testing icon (beaker) in Activity Bar
Option 2: Ctrl+Shift+P → Tasks → "Pytest: Run All Tests"
Option 3: Right-click in test file → "Run Python Tests in File"
```

### "GitHub Copilot isn't working?"
```
1. Check bottom-right status bar for Copilot icon
2. Click it to see status
3. Make sure you're signed into GitHub
4. Verify subscription: https://github.com/settings/copilot
5. If still not working: Ctrl+Shift+P → "Developer: Reload Window"
```

### "Imports not working?"
```
1. Check Python interpreter: Ctrl+Shift+P → "Python: Select Interpreter"
2. Choose the .venv interpreter
3. Make sure dependencies installed: pip install -e .
4. Reload window: Ctrl+Shift+P → "Developer: Reload Window"
```

## Next Steps

### Learn More
- **Full Setup Guide**: [docs/VSCODE_SETUP.md](VSCODE_SETUP.md)
- **Quick Reference**: [docs/VSCODE_QUICKREF.md](VSCODE_QUICKREF.md)
- **Workflows**: [docs/VSCODE_WORKFLOWS.md](VSCODE_WORKFLOWS.md)
- **Ten8t Docs**: https://ten8t.readthedocs.io/

### Try These Tasks
1. ✍️ Create your first check function
2. 🧪 Write tests for your check
3. 🐛 Debug a check with breakpoints
4. 🚀 Run one of the demo applications
5. 🤝 Ask Copilot to explain something complex

### Get Help
- **In VSCode**: `Ctrl+Alt+I` → Ask Copilot
- **GitHub Issues**: https://github.com/hucker/ten8t/issues
- **Documentation**: https://ten8t.readthedocs.io/

## The Bottom Line

**You asked: "How do I ask these questions in VSCode?"**

**Answer:**
1. Install GitHub Copilot extension (included in recommended extensions)
2. Press `Ctrl+Alt+I` to open chat
3. Type: `@workspace` followed by your question
4. Get answers about Ten8t, see examples, get code generated, understand errors

**That's it!** You now have:
- ✅ A fully configured VSCode setup
- ✅ AI assistant integrated into your editor
- ✅ Ability to ask questions and get help without leaving VSCode
- ✅ Debug, test, and develop Ten8t checks efficiently

**Start developing!** 🎉
