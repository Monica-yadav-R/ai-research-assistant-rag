# AI Research Assistant with RAG

## Project Goal
Build an AI Research Assistant that accepts research PDFs, extracts and chunks text, creates embeddings, retrieves relevant passages, and generates evidence-grounded answers with citations. The system should acknowledge when the available evidence is insufficient.

## Current Stage
Stage 1 — Project setup and foundations.

## Verified Environment
- Operating system: Windows (PowerShell)
- Python: 3.11.0
- Git: 2.56.0.windows.1
- Virtual environment: `.venv` (created and activated)
- Python executable: `.venv\Scripts\python.exe`
- Baseline packages: pip and setuptools
- Git repository: initialized; branch `master`
- GitHub remote: not configured
- No RAG libraries installed yet

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
- [x] Python and Git versions verified
- [x] Project directory verified
- [x] Tracking files created and populated
- [x] Git repository initialized
- [x] `.gitignore` created
- [x] Python virtual environment created and verified
- [x] First Python passage exercise implemented and tested
- [ ] Dependencies selected and documented
- [ ] PDF extraction implemented
- [ ] RAG pipeline implemented

## Current Task
Review and commit the verified Python practice exercise and its documentation updates.

## Next Task
Learn Python functions and write one that prints a research passage with its source and page citation.

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


### Completed in Session 1
- Created and tested `main.py` with research-passage metadata.
- Stored multiple passages in a list of dictionaries.
- Used a loop to print passage text and citations.
- Used `len(passages)` to count passages.
- Updated `LEARNING_NOTES.MD` with the new concepts.

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

### Earlier Checkpoint — Completed
- Updated learning notes and engineering decisions.
- Created and tested the first Python script for research-paper metadata.
- Subsequently learned lists, loops, passage citations, and counting with `len()`.

### Git Tracking Notes
- The repository is local; no GitHub remote is configured.
- The empty, untracked `handoff prompt` file remains untouched.
- Commit status should be checked with `git status`.

## Session 1 Progress Update — Python Data Structures

### Verified Completed
- [x] Created and ran `main.py` with research-passage metadata.
- [x] Stored multiple passage dictionaries in a list.
- [x] Accessed passages using list indexing.
- [x] Used a `for` loop to process every passage.
- [x] Printed source and page citations for each passage.
- [x] Counted passages using `len(passages)`.
- [x] Verified the output for two passages.

### Current Python Concepts
- Dictionaries and key-value pairs.
- Lists and zero-based indexing.
- Loops and indentation.
- f-strings.
- `len()` for counting list items.

### Current Architecture
- `main.py` contains a small Python practice exercise.
- PDF extraction, chunking, embeddings, vector search, and LLM generation have not been implemented.

### Next Task
Learn Python functions and use one to print a research passage with its citation.
