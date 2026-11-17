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
- Git repository: initialized; branch `master`
- GitHub remote: not configured
- Embedding library: sentence-transformers 6.2.0
- PyTorch: 2.14.1+cu130
- CUDA build: 13.0
- CUDA availability: verified True
- GPU: NVIDIA GeForce RTX 3050 Laptop GPU (4 GB reported VRAM)
- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- Embedding dimensions: 384
- Vector search library: not selected yet
- LLM integration: not implemented yet

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
- [x] PDF extraction implemented
- [x] Text chunking with overlap implemented
- [x] Embedding generation implemented
- [ ] RAG pipeline implemented
- [x] Embedding model installed and experimental generation verified
- [x] Reusable embedding module implemented and tested
- [ ] FAISS vector search implemented

## Current Task
Document and commit the tested embedding-generation component.

## Next Task
Evaluate FAISS for storing chunk embeddings and retrieving semantically relevant passages.

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

## PDF Text Extraction — Completed

**Module:** `pdf_extractor.py`

**Dependency:** PyMuPDF (`pymupdf`)

### Implemented
- Extracts text from each PDF page separately.
- Preserves source filename, one-based page number, and extracted text.
- Preserves blank pages as records with empty text.
- Validates that the path exists and has a `.pdf` extension.
- Uses a context manager to close the PDF safely.
- Allows errors for missing or corrupt PDFs to propagate to the caller.

### Automated tests
Test file: `tests/test_pdf_extractor.py`

Command:
`python -m unittest discover -s tests -v`

**Last verified result:** 5 tests passed.

Test coverage:
- Page text and metadata extraction
- Blank-page preservation
- Missing-file handling
- Incorrect file extension
- Corrupt PDF handling

### Known limitations
- Scanned PDFs requiring OCR are not supported yet.
- Testing so far uses generated sample PDFs, not a real research paper.
- Extraction quality on complex layouts, tables, and multi-column papers remains unverified.

### Next milestone
Implement text chunking and overlap while preserving source and page metadata.

## Text Chunking — Completed

**Module:** `text_chunker.py`

**Test file:** `tests/test_text_chunker.py`

### Implemented
- Splits each nonempty page into word-based chunks.
- Supports configurable chunk size and overlap.
- Preserves source filename and page number for each chunk.
- Skips blank or whitespace-only page text.
- Rejects invalid chunk-size and overlap settings.
- Stops creating chunks when the current chunk reaches the end of the page.

### Automated tests
Command: `python -m unittest discover -s tests -v`

**Last verified result:** 12 tests passed.

### Limitations
- Chunking is word-based, not token-based or sentence-aware.
- The initial defaults of 300 words and 50 words of overlap have not been evaluated against real research questions.
- Extraction and chunking have not yet been evaluated together on a real research paper.

### Next milestone
Generate embeddings for the chunks while preserving source and page metadata.

### pgvector – Document Deletion and User Isolation

- [x] Implemented document chunk deletion.
- [x] Verified deletion of document chunks.
- [x] Tested user isolation.
- [x] Verified that one user cannot access another user's data.
- [x] Cleaned up temporary test data.

Test result:
- Deleted chunks: 1
- User isolation: Verified
- pgvector deletion test: Passed