# Learning Notes — AI Research Assistant with RAG

## Session 1: Project Setup

### Environment
- Python 3.11.0 is installed.
- Git 2.56.0.windows.1 is installed.
- The project is being developed on Windows using PowerShell and VS Code.

### Concepts Learned

#### 1. Project status files
PROJECT_STATUS.md records the current stage, verified progress, and next task.

#### 2. PowerShell commands
- Get-Location: shows the current working directory.
- Get-ChildItem: lists files and directories.
- Get-Content: reads a file in the terminal.
- Test-Path: checks whether a path exists.
- git status: reports Git repository status and working-tree changes.

#### 3. Empty files
A file can exist but contain no text. Checking its Length helps confirm whether it is empty.

#### 4. Git repository
Git is installed, but the project folder is not yet initialized as a Git repository. The git status command confirmed this.

### RAG Concepts
Not yet studied in detail.

### Debugging Lessons
- Verify the current directory before running file commands.
- Check command output rather than assuming a task succeeded.
- Verify filenames carefully, including spelling and capitalization.

### Questions to Revisit
- How does retrieval-augmented generation work internally?
- What are Python virtual environments, and why do we use them?
- How does Git track project history?

## Session 1: Virtual Environment

### What Is a Virtual Environment?
A Python virtual environment provides an isolated location for a project's Python packages. This helps prevent dependency conflicts between different projects.

### Commands Practiced
- python -m venv .venv — creates the virtual environment.
- .\.venv\Scripts\Activate.ps1 — activates it in PowerShell.
- python --version — checks the Python version.
- (Get-Command python).Source — shows which Python executable PowerShell uses.
- python -m pip --version — checks pip and its installation location.
- python -m pip list — lists installed packages.
- git status — checks repository changes.

### Verified Results
- Python version: 3.11.0.
- Active interpreter: .venv\Scripts\python.exe.
- pip version: 22.3.
- Baseline packages: pip and setuptools.
- The .venv folder is ignored by Git.

### Debugging Lesson
A successful command should be followed by a check that confirms the expected result. For example, the interpreter path verified that activation changed which Python executable was being used.

### Next Learning Goal
Write and run a small Python script before introducing document-processing or RAG libraries.

## Session 1: First Python Exercise — Research Paper Metadata

### Concepts Learned
- A Python dictionary stores related information as key-value pairs.
- Dictionary keys can retrieve individual values, such as `paper_passage["source"]`, `paper_passage["page"]`, and `paper_passage["text"]`.
- An f-string combines Python values with readable text.
- Source filenames and page numbers help connect evidence to its original research paper.

### Practical Exercise
Created `main.py` with a dictionary representing one research-paper passage:
- Source: `climate_study.pdf`
- Page: `7`
- Text: `Rising temperatures can affect crop productivity.`

### Verified Results
- Ran `python main.py` successfully.
- Retrieved individual dictionary values.
- Constructed a citation string containing the source filename and page number.

### Connection to RAG
PDF extraction will eventually produce many passages. Keeping each passage's source and page metadata allows retrieved evidence to be traced back to the original document.

### Next Learning Goal
Learn how to store multiple research-paper passages in a Python list and access them one at a time.
