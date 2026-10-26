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


## Session 1: Lists, Loops, and Passage Counting

### Concepts Learned
- Lists store multiple items in order.
- List indexing starts at 0.
- Dictionaries store each passage's text and metadata.
- A `for` loop processes each passage automatically.
- `len()` counts the items in a list.
- Indentation determines whether a statement is inside or outside a loop.
- f-strings format source filenames and page numbers into readable citations.

### Practical Exercise
Updated `main.py` to store two research passages in a list. Used a loop to print each passage's text, source, and page number, then used `len(passages)` to print the total count.

### Verified Results
- The script printed both passages and their citations.
- The script printed the total count once, after the loop.
- The observed count was `2`.

### Connection to RAG
A RAG application needs to manage multiple passages retrieved from research papers. Lists and loops help process these passages, while source and page metadata support traceable citations.

### Next Learning Goal
Learn Python functions and use one to print a research passage with its citation.

## Session: PDF Text Extraction

### Goal
Build a reusable component that extracts text from PDF research papers and preserves the metadata needed for citations.

### Implementation
- File: `pdf_extractor.py`
- Library: PyMuPDF
- Function: `extract_pdf_pages(path: str) -> list[dict]`
- Test file: `tests/test_pdf_extractor.py`

Each extracted page is represented as a dictionary containing:
- `source`: PDF filename
- `page`: one-based page number
- `text`: extracted page text

### Engineering lessons

**1. Preserve source metadata**

Page numbers and filenames must travel with the text so that later retrieval can identify the original evidence.

**2. Use a context manager**

`with pymupdf.open(path) as doc:` ensures the document is closed when processing exits the block, including when an exception occurs.

**3. Preserve blank pages during extraction**

A blank page produces an empty string. We preserve its record to retain the original document's page numbering. Empty text can be filtered during a later processing stage.

**4. Validate input paths**

`Path.is_file()` checks whether the path refers to an existing file. Checking `Path.suffix.lower()` validates the extension, but does not guarantee that the file is a valid PDF.

**5. Handle errors deliberately**

Missing files, incorrect extensions, and corrupt PDF content are different failure cases. Letting errors propagate keeps failures visible to the calling application.

**6. Write specific automated tests**

A broad `assertRaises(Exception)` can pass because of unrelated errors. Testing for `pymupdf.FileDataError` makes the corrupt-PDF test more precise.

### Verified test result

Command:
`python -m unittest discover -s tests -v`

Result: 5 tests passed in the latest verified run.

The tests cover metadata extraction, blank-page preservation, missing files, incorrect extensions, and corrupt PDF content.

### Limitations

- Scanned PDFs requiring OCR have not been implemented.
- The tests use generated PDFs; extraction from real research papers remains to be verified.
- Complex layouts and tables have not been evaluated.

### Next learning milestone: Chunking and overlap

Learn how to divide extracted text into smaller passages suitable for embedding and retrieval. Preserve the source filename and page number for each chunk so that retrieved evidence can be cited later.

## Session: Text Chunking and Overlap

### Goal
Split extracted PDF page text into smaller passages while preserving citation metadata.

### Concepts learned
- `str.split()` converts text into a list of whitespace-separated words.
- Python slicing selects a portion of a list using `words[start:end]`.
- The step size is calculated as `chunk_size - overlap`.
- Overlap repeats words between neighboring chunks to help retain context.
- Each chunk retains the original source filename and page number.
- Empty page text is skipped.
- Invalid chunk-size and overlap settings raise `ValueError`.

### Implementation
- Module: `text_chunker.py`
- Function: `chunk_pages()`
- Tests: `tests/test_text_chunker.py`

### Verified test result
Command: `python -m unittest discover -s tests -v`

Result: 12 tests passed in the latest verified run, including PDF extraction and chunking tests.

### Limitations
- Word-based chunking does not guarantee alignment with model token limits or sentence boundaries.
- Chunk size and overlap remain initial settings and require evaluation.

### Next learning milestone
Understand embedding models and how they represent text as numerical vectors for semantic search.

## Session: Embeddings and GPU Inference

### Concepts learned
- An embedding model converts text into a numerical vector that represents aspects of its meaning.
- `sentence-transformers/all-MiniLM-L6-v2` produces vectors with 384 dimensions.
- Semantic search compares a question's vector with document-chunk vectors to find potentially relevant passages.
- Cosine similarity measures the similarity in vector direction. It is not a probability that an answer is correct.
- Document embeddings can be reused until the underlying text or embedding model changes.
- Sentence Transformers can run on a CPU or a supported NVIDIA GPU.
- Batch size affects processing speed and memory usage.

### Verified embedding experiment
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Device: `cuda:0`
- Three example sentences produced an embedding array with shape `(3, 384)`.
- Similarity between the two learning-related sentences: `0.5945`.
- Similarity between a learning-related sentence and the photosynthesis sentence: `0.0413`.
- These scores apply to this experiment; they are not universal relevance thresholds.

### CPU versus GPU benchmark
- Script: `benchmark_embeddings.py`
- Workload: 1,000 synthetic repeated text inputs, batch size 32.
- CPU time: 1.235 seconds.
- GPU time: 0.457 seconds.
- Observed speedup: 2.71x for this benchmark.
- This result does not guarantee the same speedup for real research papers or other batch sizes.

### Next milestone
Implement a reusable embedding module that converts text chunks into vectors while preserving their source and page metadata.

## Session: Reusable Embedding Generation

### Implementation
- Created `embedding_generator.py`.
- `load_embedding_model(device=None)` loads the configured Sentence Transformer model.
- `generate_embeddings(chunks, model)` embeds chunk text and returns new dictionaries containing the original metadata plus an `embedding` field.
- Embeddings are normalized using `normalize_embeddings=True`.
- Input validation rejects non-dictionary chunks, missing text, and empty or non-string text.
- The model is passed into the embedding function so it can be reused rather than reloaded for every call.

### Testing and verification
- Added `tests/test_embedding_generator.py`.
- Seven embedding unit tests passed.
- Full test suite: 19 tests passed.
- Real-model integration check: one chunk produced a 384-dimensional vector.
- Source and page metadata were preserved.
- The normalized vector's L2 norm was 1.0.
- GPU inference succeeded using CUDA.

### Limitations
- Retrieval quality has not been evaluated yet.
- Real research-paper workloads have not been benchmarked through the full pipeline.
- FAISS integration is not implemented yet.

### Next milestone
Evaluate FAISS for vector storage and semantic retrieval.
