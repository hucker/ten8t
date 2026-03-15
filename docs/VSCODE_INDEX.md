# VSCode Integration Documentation - Index

**Want to develop Ten8t locally in VSCode with AI coding assistants?** Start here!

## 📚 Documentation Overview

This folder contains everything you need to work with Ten8t in Visual Studio Code.

### **Start Here** 👉 [VSCODE_GETTING_STARTED.md](VSCODE_GETTING_STARTED.md)
The quickest path from "how do I use VSCode?" to "I'm coding with AI assistance!"
- 5-minute setup
- How to ask questions in VSCode with GitHub Copilot
- Common tasks and troubleshooting

### **Quick Reference** 📋 [VSCODE_QUICKREF.md](VSCODE_QUICKREF.md)
Keyboard shortcuts, commands, and quick answers
- Keep this open while coding
- All shortcuts in one place
- Task cheat sheet

### **Complete Guide** 📖 [VSCODE_SETUP.md](VSCODE_SETUP.md)
In-depth documentation for VSCode + Ten8t development
- Detailed setup instructions
- Configuration explanations
- Advanced features
- Best practices

### **Workflows** 🔄 [VSCODE_WORKFLOWS.md](VSCODE_WORKFLOWS.md)
Step-by-step examples for common development tasks
- Creating new checks
- Debugging
- Writing tests
- Integration patterns

## 🚀 Super Quick Start

```bash
git clone https://github.com/hucker/ten8t.git && cd ten8t && code .
# Install extensions when prompted
python -m venv .venv && source .venv/bin/activate
pip install -e .
# Ctrl+Shift+P → "Python: Select Interpreter" → .venv
# Press Ctrl+Alt+I → Type: @workspace How do I create a check?
```

## 🤖 The Key: Using AI in VSCode

**You asked: "How do I ask these questions in VSCode?"**

**Answer:**
1. Install GitHub Copilot extension (VSCode prompts you automatically)
2. Press `Ctrl+Alt+I` to open chat
3. Type `@workspace` before your question
4. Get instant help about Ten8t!

**Example questions:**
```
@workspace How does Ten8t work?
@workspace Create a Ten8t check for file validation
/explain (select code first)
/tests Generate tests for this function
```

## 📁 Configuration Files

The repo includes `.vscode/` folder with:
- **launch.json** - Debug configurations
- **tasks.json** - One-click commands
- **settings.json** - Python & Ten8t settings
- **extensions.json** - Recommended extensions

## 💡 What This Setup Gives You

✅ Debug Ten8t checks with breakpoints  
✅ Ask AI questions without leaving editor  
✅ Run tests with one click  
✅ Auto-format code on save  
✅ Smart code completion  
✅ Integrated terminal and tasks  

## 🎯 Choose Your Path

- **I want to start NOW** → [VSCODE_GETTING_STARTED.md](VSCODE_GETTING_STARTED.md)
- **I need a quick reference** → [VSCODE_QUICKREF.md](VSCODE_QUICKREF.md)
- **I want complete documentation** → [VSCODE_SETUP.md](VSCODE_SETUP.md)
- **Show me examples** → [VSCODE_WORKFLOWS.md](VSCODE_WORKFLOWS.md)

---

**Questions?** Press `Ctrl+Alt+I` in VSCode and ask Copilot! 🚀
