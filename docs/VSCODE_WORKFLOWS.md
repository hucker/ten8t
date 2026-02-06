# VSCode Workflow Examples for Ten8t

This document provides step-by-step workflow examples for common Ten8t development tasks in VSCode with GitHub Copilot.

## Table of Contents
1. [First Time Setup](#first-time-setup)
2. [Creating a New Ten8t Check](#creating-a-new-ten8t-check)
3. [Debugging a Failing Check](#debugging-a-failing-check)
4. [Writing Tests with Copilot](#writing-tests-with-copilot)
5. [Integrating Ten8t with Your Application](#integrating-ten8t-with-your-application)

---

## First Time Setup

### Step 1: Clone and Open Repository
```bash
# Clone the repository
git clone https://github.com/hucker/ten8t.git
cd ten8t

# Open in VSCode
code .
```

### Step 2: Install Recommended Extensions
When VSCode opens, you'll see a notification in the bottom-right:
```
Do you want to install the recommended extensions for this repository?
```
Click **"Install All"** or **"Show Recommendations"** to install:
- Python
- Pylance
- Python Debugger
- Ruff
- GitHub Copilot
- GitHub Copilot Chat
- And more...

### Step 3: Set Up Python Environment
```bash
# In VSCode terminal (Ctrl+` or View → Terminal)
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install Ten8t in development mode
pip install -e .
pip install -r requirements.txt
```

### Step 4: Select Python Interpreter
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Select Interpreter"
3. Choose the `.venv` interpreter (should show in the list)
4. Confirm by checking the status bar (bottom-right) shows `.venv`

### Step 5: Verify Setup
Press `F5` and select "Python: Ten8t CLI (Module)" - it should run without errors!

---

## Creating a New Ten8t Check

Let's create a check that validates API response times.

### Step 1: Ask Copilot to Help You Start
1. Create a new file: `my_api_checks.py` in `src/ten8t/examples/`
2. Press `Ctrl+I` (inline chat)
3. Type:
   ```
   Create a Ten8t check function that validates an API endpoint responds within 2 seconds
   Use the requests library and include proper error handling
   ```
4. Review the generated code and accept suggestions

### Step 2: Refine with Copilot
If the initial code needs adjustments:
1. Select the function
2. Press `Ctrl+I`
3. Ask: "Add retry logic with @attempt decorator for 3 attempts"
4. Or: "Add more detailed error messages to the Ten8tResult"

### Step 3: Test Your Check
**Option A: Use Debug Mode**
1. Set a breakpoint (click left of line number)
2. Press `F5` → Select "Python: Current File"
3. Step through code with `F10` (Step Over) and `F11` (Step Into)

**Option B: Use Task**
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Ten8t: Run Current File"
4. View output in terminal

### Step 4: Format and Verify
Code will auto-format on save, but you can also:
1. Press `Shift+Alt+F` to format manually
2. Run task "Lint: Run Ruff" to check for issues

---

## Debugging a Failing Check

You have a Ten8t check that's failing unexpectedly. Here's how to debug it:

### Step 1: Run in Debug Mode
1. Open the file with the failing check
2. Set breakpoint on the first line of the check function
3. Press `F5` → "Python: Ten8t CLI (Module)"
4. When execution stops at breakpoint, inspect variables

### Step 2: Ask Copilot for Help
1. While at the breakpoint, press `Ctrl+Alt+I` (open chat panel)
2. Select the problematic code
3. Ask:
   ```
   @workspace Why would this check fail?
   The error I'm seeing is: [paste error message]
   ```
4. Or simply: `/fix` with the code selected

### Step 3: Use Debug Console
While debugging:
1. Click "Debug Console" tab (bottom panel)
2. Type expressions to inspect:
   ```python
   # Check variable values
   my_variable
   
   # Test function calls
   pathlib.Path("my_file.txt").exists()
   
   # Evaluate complex expressions
   [x for x in my_list if x > 10]
   ```

### Step 4: Step Through Execution
Use these keys while debugging:
- `F5` - Continue to next breakpoint
- `F10` - Step over (execute current line)
- `F11` - Step into (enter function call)
- `Shift+F11` - Step out (return from function)
- `F9` - Toggle breakpoint on current line

### Step 5: Fix and Verify
1. Make your fixes based on what you found
2. Press `Shift+F5` to stop debugging
3. Press `F5` again to re-run with fixes
4. Remove breakpoints when done (click red dot)

---

## Writing Tests with Copilot

Let's write pytest tests for a Ten8t check function.

### Step 1: Create Test File
1. Create `test/test_my_checks.py`
2. Press `Ctrl+I`
3. Ask:
   ```
   Create pytest tests for the Ten8t check functions in src/ten8t/examples/my_api_checks.py
   Include tests for success case, failure case, and edge cases
   Use pytest fixtures for setup
   ```

### Step 2: Review and Refine Tests
1. Review generated tests
2. If you need more coverage, select a function and ask:
   ```
   /tests Add more test cases for this function including error conditions
   ```

### Step 3: Run Tests
**Using Testing Panel:**
1. Click Testing icon in Activity Bar (left side)
2. Click refresh icon if tests don't appear
3. Click green play button next to test to run it
4. Click bug icon to debug a test

**Using Tasks:**
1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select "Pytest: Run Current Test File"

### Step 4: Check Coverage
1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select "Pytest: Run with Coverage"
3. View coverage report in terminal
4. Open `htmlcov/index.html` in browser for detailed report

### Step 5: Ask Copilot About Test Quality
```
@workspace Do my tests cover all the important cases for this check?
Are there any edge cases I'm missing?
```

---

## Integrating Ten8t with Your Application

Let's integrate Ten8t into a FastAPI application.

### Step 1: Ask Copilot for Integration Pattern
1. Create new file: `my_app.py`
2. Press `Ctrl+I`
3. Ask:
   ```
   @workspace Show me how to integrate Ten8t checks into a FastAPI application
   Create an endpoint that runs checks and returns JSON results
   Use the examples from the Ten8t codebase
   ```

### Step 2: Explore Existing Examples
1. Press `Ctrl+P` (Quick Open)
2. Type `ten8t_api.py` to find the existing API implementation
3. Press `F12` on interesting functions to see definitions
4. Ask Copilot:
   ```
   @workspace Explain how ten8t_api.py works
   #file:src/ten8t/cli/ten8t_api.py
   ```

### Step 3: Implement Your Integration
1. Write your integration code
2. Use `Ctrl+Space` for autocomplete
3. Use `F12` to jump to Ten8t function definitions
4. Ask Copilot for help with specific patterns:
   ```
   How do I filter Ten8t results by tag?
   Show me how to convert Ten8t results to a custom format
   ```

### Step 4: Test Your Integration
**Start the API Server:**
1. Press `F5` → "Python: Ten8t API Server"
2. Or use Task: "Ten8t: Start API Server"
3. Server will start on http://localhost:8000

**Test Endpoints:**
```bash
# In a new terminal
curl http://localhost:8000/
curl http://localhost:8000/docs  # OpenAPI documentation
```

**Debug the API:**
1. Set breakpoints in your endpoint handlers
2. Make a request to the API
3. Debug as normal when breakpoint hits

### Step 5: Iterate with Copilot
As you develop, keep asking questions:
```
@workspace How do I handle errors in Ten8t checks gracefully?
Show me best practices for Ten8t result serialization
How can I run Ten8t checks asynchronously?
```

---

## Pro Tips for VSCode + Copilot + Ten8t

### 1. Use @workspace for Contextual Help
Always prefix questions with `@workspace` when asking about Ten8t:
```
@workspace Where is the Ten8tResult class defined?
@workspace Show me examples of using categories decorator
@workspace How does the environment system work?
```

### 2. Reference Specific Files
Use `#file:` to reference specific files:
```
#file:src/ten8t/ten8t_checker.py Explain the run_all method
```

### 3. Select Code Before Asking
For more precise help:
1. Select a function or code block
2. Press `Ctrl+I`
3. Use `/explain`, `/fix`, or `/tests`

### 4. Iterate on Responses
Don't accept the first answer - iterate:
```
# First question
Create a Ten8t check for database connectivity

# Follow-up
Add connection pooling to this check

# Refinement
Make the timeout configurable via environment
```

### 5. Learn Keyboard Shortcuts
Master these for productivity:
- `Ctrl+I` - Quick inline chat
- `Ctrl+Alt+I` - Full chat panel
- `F5` - Start debugging
- `F12` - Go to definition
- `Ctrl+P` - Quick open file
- `Ctrl+Shift+F` - Search in files

### 6. Use Split Editor
1. Press `Ctrl+\` to split editor
2. Keep documentation open on one side
3. Code on the other side
4. Or: Keep test file and implementation side-by-side

### 7. Pin Important Files
Right-click on file tabs and select "Pin" for:
- Your main check files
- Test files you're working on
- Documentation references

### 8. Keep Terminal Visible
1. Press `Ctrl+`` to toggle terminal
2. Keep it open at bottom for quick command access
3. Run tests, lint, format without leaving VSCode

---

## Common Copilot Questions for Ten8t

Here's a collection of useful questions to ask Copilot:

### Understanding Ten8t
```
@workspace What is the purpose of the Ten8tChecker class?
@workspace Explain the difference between check_f, modules, and packages parameters
@workspace How does the categories decorator work?
@workspace What is a Ten8tResult and what fields does it have?
```

### Creating Checks
```
Create a Ten8t check that validates file permissions
Create a Ten8t check that queries a REST API
Create a Ten8t check that verifies database records exist
Create a Ten8t check with custom scoring logic
```

### Debugging and Fixing
```
/explain this Ten8t check function
/fix this failing check
Why is my Ten8t result showing as failed?
How do I add better error messages to my checks?
```

### Testing
```
/tests Generate pytest tests for this Ten8t check
How do I mock API calls in Ten8t check tests?
Create a pytest fixture for Ten8t checker setup
```

### Integration
```
@workspace Show me how to integrate Ten8t with Streamlit
@workspace How do I run Ten8t checks from a cron job?
@workspace Best way to serialize Ten8t results to JSON
@workspace How to filter and format Ten8t results for a dashboard
```

### Advanced Topics
```
@workspace How does Ten8t threading work?
@workspace Explain Ten8t's retry/attempt mechanism
@workspace How do I create custom Ten8t result strategies?
@workspace Show me how to extend Ten8t with custom rules
```

---

## Troubleshooting Workflow

If something isn't working, follow this checklist:

### 1. Python Environment Issues
```
# Verify Python interpreter
Ctrl+Shift+P → "Python: Select Interpreter" → Choose .venv

# Check PYTHONPATH
@workspace Why are my imports not working?

# Reinstall dependencies
pip install -e . --force-reinstall
```

### 2. Test Discovery Issues
```
# Reload window
Ctrl+Shift+P → "Developer: Reload Window"

# Check pytest configuration
@workspace Why aren't my tests being discovered?

# Verify test naming
# Tests must be in files named test_*.py with functions named test_*
```

### 3. Copilot Not Responding
```
# Check status bar (bottom-right) for Copilot icon
# Click icon to see status
# Sign in if needed

# Verify subscription
Visit: https://github.com/settings/copilot

# Reload extension
Ctrl+Shift+P → "Developer: Reload Window"
```

### 4. Tasks Not Working
```
# Make sure virtual environment is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Try running command manually
python -m ten8t src/ten8t/examples

# Ask Copilot
@workspace This task is failing: [task name]. What's wrong?
```

---

## Next Steps

Now that you're set up, try these:

1. **Explore Examples**: Open `src/ten8t/examples/` and read through existing checks
2. **Run Demos**: Try the Streamlit, FastAPI, or Rich demos from the tasks
3. **Create Your First Check**: Make a check for something you want to monitor
4. **Write Tests**: Practice TDD with Copilot's help
5. **Share**: Contribute your checks back to the Ten8t project!

## Need Help?

- **In VSCode**: Press `Ctrl+Alt+I` and ask Copilot
- **Documentation**: https://ten8t.readthedocs.io/
- **GitHub**: https://github.com/hucker/ten8t/issues
- **Quick Reference**: See [VSCODE_QUICKREF.md](VSCODE_QUICKREF.md)

---

**Happy Coding!** 🚀 Remember: When in doubt, ask Copilot with `@workspace`!
