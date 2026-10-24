# AI Research Assistant with RAG

## Project Goal
Build an AI Research Assistant that accepts research PDFs, extracts and chunks text, creates embeddings, retrieves relevant passages, and generates evidence-grounded answers with citations. The system should acknowledge when the available evidence is insufficient.

## Current Stage
Stage 1 — Project setup and foundations.

## Verified Environment
- Operating system: Windows (PowerShell)
- Python: 3.11.0
- Git: 2.56.0.windows.1
- Project folder: AI Research Assisstant with RAG
- Git repository: Not initialized in this folder (verified by git status).

## Architecture Plan
1. PDF text extraction and page metadata
2. Text chunking and overlap
3. Embedding generation
4. FAISS vector search
5. Evidence-grounded LLM answers and citations
6. Streamlit interface
7. FastAPI architecture
8. Evaluation, testing, security, and failure analysis
9. Deployment and documentation

## Progress
- [x] Python version checked
- [x] Git version checked
- [x] Project directory verified
- [x] Existing tracking files inspected
- [ ] Tracking files populated and standardized
- [ ] Git repository initialized
- [ ] Python virtual environment created
- [ ] Dependencies selected and documented
- [ ] First implementation task completed

## Current Task
Populate project documentation and prepare Git safely.

## Next Task
Standardize the tracking filenames, initialize Git, and verify the repository state.

## Important Rules
- Implement one small step at a time.
- Understand code before using it.
- Test behavior instead of assuming it works.
- Record technical decisions and debugging lessons.
- Prefer free and local tools where practical.
- Do not claim a task is complete until it is verified.

## Session 1 Progress Update

### Verified Completed
- [x] Python 3.11.0 and Git 2.56.0 verified.
- [x] Project documentation created and populated.
- [x] Git initialized and first commit created: f86516f.
- [x] .gitignore created and verified.
- [x] Python virtual environment created and activated.
- [x] pip verified inside the virtual environment.
- [x] Confirmed .venv is ignored by Git.

### Environment Details
- Virtual environment: .venv
- Activation command: .\.venv\Scripts\Activate.ps1
- Python executable: .venv\Scripts\python.exe
- Installed packages at baseline: pip, setuptools
- No RAG libraries installed yet.

### Current Limitations
- Repository is local; GitHub remote is not configured.
- An empty, untracked file named "handoff prompt" remains.
- RAG implementation has not started.

### Next Task
Update learning notes and engineering decisions, then begin the first small Python exercise.

## Session 1 Progress Update — First Python Exercise

### Verified Completed
- [x] Created `main.py` with a research-paper passage dictionary.
- [x] Stored the source filename, page number, and passage text.
- [x] Retrieved individual values using dictionary keys.
- [x] Used an f-string to format a source-and-page citation.
- [x] Ran `python main.py` and observed the expected citation output.
- [x] Added the exercise and its RAG connection to `LEARNING_NOTES.MD`.

### Current Python Concepts
- Dictionaries and key-value pairs.
- Accessing values using dictionary keys.
- f-strings for readable output.

### Current Git State
- The documentation changes and `main.py` need to be reviewed and committed.
- The untracked `handoff prompt` file remains untouched.

### Completed in Session 1
- Updated learning notes and engineering decisions.
- Created and tested the first Python script for research-paper metadata.

### Next Task
Learn how a Python list can store multiple research-paper passages, then access each passage individually.
