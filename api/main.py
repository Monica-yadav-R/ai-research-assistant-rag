import logging
from fastapi import FastAPI,File,UploadFile,HTTPException,Depends,status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

import hashlib
from .schemas import (
    PDFInputResponse,
    DocumentResponse,
    DocumentUpdate,
    QuestionResponse,
    SourceReference,
    QuestionRequest,
    UserRegister,
    UserResponse
)
from pdf_extractor import pdf_to_chunks
from api.model import Document,User
from api.database import init_db,get_db
from embedding_generator import (
    load_embedding_model,
    generate_embeddings
)
from retrieval_experiment import(
    question_embedding,
    llm_generation,
    calculate_sha256
)
from api.pgvector_store import (
    store_chunks as store_pgvector_chunks,
    search_chunks as search_pgvector_chunks,
    delete_document_chunks as delete_pgvector_chunks
)
from fastapi.security import OAuth2PasswordRequestForm

from api.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password
)

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True,exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024 #20 MB
logger = logging.getLogger(__name__)

@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    # Check whether username or email already exists
    existing_user = db.scalar(
        select(User).where(
            (User.username == user_data.username) |
            (User.email == user_data.email)
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered."
        )

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create the new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered."
        )

    return new_user

@app.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(user_id=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800
    }

@app.get("/auth/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@app.post(
    "/api/v1/documents/upload",
    response_model=PDFInputResponse
)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Track resources so failed uploads can be cleaned up.
    file_path = None
    document_id = None  

    document_record_created = False
    chunks_may_exist = False

    # Cleanup function: attempts to undo a failed upload.
    def cleanup_failed_upload():

        # 1. Remove pgvector chunks if storage was attempted.
        if chunks_may_exist and document_id is not None:
            try:
                delete_pgvector_chunks(
                    document_id=document_id,
                    user_id=current_user.id
                )
            except Exception:
                logger.exception(
                    "Failed to clean up pgvector chunks for document %s",
                    document_id
                )

        # 2. Remove SQLite document record.
        if document_record_created:
            try:
                db.query(Document).filter(
                    Document.id == document_id,
                    Document.user_id == current_user.id
                ).delete(synchronize_session=False)

                db.commit()

            except Exception:
                db.rollback()
                logger.exception(
                    "Failed to clean up SQLite record for document %s",
                    document_id
                )

        # 3. Remove uploaded PDF.
        if file_path is not None and file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                logger.exception(
                    "Failed to delete uploaded PDF: %s",
                    file_path
                )

    try:

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is missing."
            )

        # Handle both Windows and Linux path separators.
        safe_filename = Path(
            file.filename.replace("\\", "/")
        ).name

        if Path(safe_filename).suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        # Read one byte beyond the limit to detect oversized files.
        content = await file.read(MAX_FILE_SIZE + 1)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds the 10 MB limit."
            )

        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file content."
            )

        content_hash = hashlib.sha256(content).hexdigest()

        existing_document = db.scalar(
            select(Document).where(
                Document.user_id == current_user.id,
                Document.content_hash == content_hash
            )
        )

        if existing_document:
            raise HTTPException(
                status_code=409,
                detail="You have already uploaded this document."
            )


        model = load_embedding_model()


        document_id = str(uuid4())

        user_upload_dir = UPLOAD_DIR / current_user.id
        user_upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = user_upload_dir / (
            f"{document_id}_{safe_filename}"
        )

        file_path.write_bytes(content)


        try:
            result = pdf_to_chunks(file_path)

            if not result:
                raise ValueError("PDF contains no extractable text.")

        except Exception:
            logger.exception(
                "PDF extraction failed for document %s",
                document_id
            )

            raise HTTPException(
                status_code=422,
                detail="Could not extract readable text from this PDF."
            )

        try:
            embedded_chunks = generate_embeddings(
                chunks=result,
                model=model
            )

            if not embedded_chunks:
                raise ValueError("Embedding generation returned no chunks.")

        except Exception:
            logger.exception(
                "Embedding generation failed for document %s",
                document_id
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to generate document embeddings."
            )

        total_chunks = len(result)

        total_pages = len({
            chunk["page"] for chunk in result
        })

        document = Document(
            id=document_id,
            user_id=current_user.id,
            filename=safe_filename,
            file_path=str(file_path),
            status="processing",
            total_pages=total_pages,
            total_chunks=total_chunks,
            content_hash=content_hash
        )

        try:
            db.add(document)
            db.commit()
            db.refresh(document)

            document_record_created = True

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=409,
                detail="This document has already been uploaded."
            )

        # Set this before calling store_chunks because it
        # might partially insert chunks and then fail.
        chunks_may_exist = True

        store_pgvector_chunks(
            document_id=document_id,
            user_id=current_user.id,
            embedded_chunks=embedded_chunks
        )

        document.status = "processed"

        db.commit()
        db.refresh(document)

        return PDFInputResponse(
            document_id=document_id,
            filename=safe_filename,
            status="processed",
            total_pages=total_pages,
            total_chunks=total_chunks,
            message="PDF uploaded successfully."
        )

    except HTTPException:
        db.rollback()
        cleanup_failed_upload()
        raise

    except Exception:
        db.rollback()

        logger.exception(
            "Unexpected upload failure for user %s",
            current_user.id
        )

        cleanup_failed_upload()

        raise HTTPException(
            status_code=500,
            detail="Document upload failed. Please try again."
        )

    finally:
        # Always close the uploaded file, including on failure.
        await file.close()

@app.get("/all_documents", response_model=list[DocumentResponse])
def get_alldocuments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = db.execute(
        select(Document).where(
            Document.user_id == current_user.id
        )
    ).scalars().all()

    if not documents:
        raise HTTPException(
            status_code=404,
            detail="Documents are empty"
        )

    return documents

@app.get("/get_document/{document_id}", response_model=DocumentResponse)
def get_docuemnts(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


@app.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.execute(
        select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    ).scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    file_path = Path(document.file_path)

    # Step 1: Delete pgvector chunks
    try:
        deleted_chunks = delete_pgvector_chunks(
            document_id=document_id,
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document chunks: {str(e)}"
        )

    # Step 2: Delete SQLite record
    try:
        db.delete(document)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document record: {str(e)}"
        )

    # Step 3: Delete uploaded PDF
    try:
        if file_path.exists():
            file_path.unlink()
    except OSError as e:
       # Database and pgvector are already updated.
        raise HTTPException(
            status_code=500,
            detail=(
                "Document record and chunks were deleted, "
                f"but the PDF file could not be deleted: {str(e)}"
            )
        )

    return {
        "detail": "Document deleted successfully",
        "document_id": document_id,
        "deleted_chunks": deleted_chunks
    }


@app.put("/update/document/{document_id}",response_model=DocumentResponse)
def update_document(document_id:str,update_data:DocumentUpdate,db:Session=Depends(get_db),current_user: User = Depends(get_current_user)):
    result = db.execute(select(Document).where(Document.id == document_id,Document.user_id == current_user.id))
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    update_fields = update_data.model_dump(exclude_unset=True)
    for field,value in update_fields.items():
        setattr(document,field,value)
    try:
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update document."
        )

@app.get("/documents/{document_id}/status")
def get_status(document_id:str,db:Session=Depends(get_db),current_user: User = Depends(get_current_user)):
    result = db.execute(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not Found"
        )
    return {
        "document_id": document.id,
        "status":document.status
    }


#--------------LLM answer retrieval
@app.post("/api/v1/question-answer",response_model=QuestionResponse)
def ask_question(
    request:QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question=request.question
    document_id=request.document_id
    if document_id is not None:
        document = db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
        ).scalar_one_or_none()

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

    try:
        model = load_embedding_model()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load the model: {str(error)}"
        )
    try:
        query_embedding = question_embedding(question,model)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate query embedding: {str(e)}"
        )
    try:
        results = search_pgvector_chunks(
            question_embedding=query_embedding,
            user_id=current_user.id,
            top_k=3,
            document_id=document_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search the chunks: {str(e)}"
        )
    try:
        answer= llm_generation(
            question=question,
            results=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate the answer: {str(e)}"
        )
    return QuestionResponse(
        answer=answer,
        sources=[
            SourceReference(
                source=result["source"],
                page=result["page"]
            )
            for result in results
        ],
        limitations=None
    )