# Engineering Decisions — AI Research Assistant with RAG

## Decision 1: Learning and implementation approach
- Choice: Build incrementally, with explanations, small coding tasks, and tests.
- Reason: Understand the implementation and develop independent debugging skills.
- Status: Accepted.

## Decision 2: Prefer free and local tools
- Choice: Prefer free, locally runnable tools when practical.
- Reason: Keep development costs low and understand the underlying components.
- Trade-off: Local models may require more memory and computing resources.
- Status: Accepted.

## Decision 3: Preserve source metadata
- Choice: Track source document names and page numbers during PDF processing and preserve them in every generated chunk.
- Reason: Answers need traceable citations to the original research papers.
- Verification: Implemented in `pdf_extractor.py` and `text_chunker.py`; automated tests verify metadata preservation.
- Status: Accepted and implemented.

## Decision 4: Ground answers in retrieved evidence
- Choice: Answers should use relevant retrieved passages and acknowledge insufficient evidence.
- Reason: Reduce unsupported claims and improve answer traceability.
- Status: Planned; implementation not started.

## Decision 5: Select libraries and models after evaluation
- Choice: Do not finalize the embedding model, vector index configuration, or LLM before considering requirements and available hardware.
- Reason: Make deliberate, documented engineering choices instead of adding unnecessary dependencies.
- Status: Pending evaluation.

## Decision 6: Verify before marking work complete
- Choice: Test commands and code and record observed results.
- Reason: Keep project progress accurate and make debugging reproducible.
- Status: Accepted.

## Decision 7: Use a project-specific Python virtual environment
- Choice: Use Python venv in the .venv directory.
- Reason: Isolate project dependencies and reduce conflicts with other Python projects.
- Cost: No additional environment-management package is required.
- Verification: Confirmed that the active interpreter is .venv\Scripts\python.exe.
- Status: Accepted and verified.

## Decision 8: Delay installing RAG dependencies
- Choice: Do not install PDF, embedding, vector-search, or LLM libraries before the initial environment checks and architecture planning.
- Reason: Keep the starting environment simple and make dependency changes easier to diagnose.
- Status: Accepted; dependency selection is pending.


## Decision 9: Initial word-based chunking
- Choice: Split each nonempty page into chunks using a configurable word count and overlap.
- Initial defaults: 300 words per chunk and 50 words of overlap.
- Reason: Provide a simple, testable baseline before introducing token-aware or sentence-aware chunking.
- Trade-off: Word counts do not correspond exactly to model token limits, and the initial settings have not been evaluated on real research papers.
- Verification: `text_chunker.py` implemented; chunking and PDF extraction tests passed in the latest verified run (12 tests).
- Status: Accepted as an initial baseline; evaluation pending.

## Decision 10: Initial embedding model

- **Choice:** Use `sentence-transformers/all-MiniLM-L6-v2` as the initial local embedding model.
- **Reason:** It provides a compact baseline for semantic search without requiring a paid embedding API.
- **Verification:** The model loaded successfully, generated 384-dimensional vectors, and was used in a cosine-similarity experiment.
- **Trade-off:** Its retrieval quality still needs to be evaluated on real research papers and questions.
- **Status:** Accepted as the initial baseline; evaluation pending.

## Decision 11: Use GPU for local embedding experiments

- **Choice:** Use CUDA-enabled PyTorch and the NVIDIA GPU when appropriate.
- **Environment:** PyTorch `2.14.1+cu130`; NVIDIA GeForce RTX 3050 Laptop GPU, reported 4 GB VRAM.
- **Verification:** CUDA was available, and Sentence Transformers reported `cuda:0`.
- **Benchmark:** On the tested synthetic workload, CPU took 1.235 seconds and GPU took 0.457 seconds.
- **Trade-off:** Performance depends on workload and batch size; GPU memory is limited.
- **Status:** Accepted for experimentation; real-paper performance remains unverified.

## Decision 12: Reusable embedding-generation component

- **Choice:** Implement embedding generation in `embedding_generator.py`, separate from PDF extraction and chunking.
- **Model:** `sentence-transformers/all-MiniLM-L6-v2`.
- **Output:** New chunk dictionaries containing the original fields and a normalized embedding vector.
- **Model lifecycle:** Load the model separately and pass the instance into the embedding function for reuse.
- **Validation:** Reject malformed chunks before embedding.
- **Verification:** Seven embedding unit tests passed; the complete suite passed 19 tests; a real-model GPU experiment produced a 384-dimensional normalized vector.
- **Trade-off:** The initial model is a baseline. Its retrieval quality must be evaluated before treating it as the final choice.
- **Status:** Implemented and tested; commit pending.
