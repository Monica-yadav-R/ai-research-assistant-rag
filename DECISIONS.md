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
- Choice: Track source document names and page numbers during PDF processing.
- Reason: Answers need traceable citations to the original research papers.
- Status: Planned; implementation not started.

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
