from pydantic import BaseModel,Field,ConfigDict
from pathlib import Path
from datetime import datetime
import mimetypes

class PDFInputResponse(BaseModel):
    document_id: str = Field(description="Unique document identifier")
    filename: str = Field(description="Uploaded PDF filename")
    status: str = Field(description="Document processing status")
    total_pages: int = Field(ge=0, description="Total pages extracted")
    total_chunks: int = Field(ge=0, description="Total chunks generated")
    message: str = Field(description="Processing result message")

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_path: str
    status: str
    total_pages: int
    total_chunks: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

from pydantic import BaseModel, Field

class DocumentUpdate(BaseModel):
    filename: str | None = None
    status: str | None = None
    total_pages: int | None = Field(default=None, ge=0)
    total_chunks: int | None = Field(default=None, ge=0)

class QuestionRequest(BaseModel):
    question:str = Field(
        min_length=3,
        description="Question about the research paper"
    )
    document_id: str|None=Field(
        default=None,
        description="Optional document ID to restrict the search"
    )

class SourceReference(BaseModel):
    source:str
    page:int

class QuestionResponse(BaseModel):
    answer:str
    sources:list[SourceReference]
    limitations:str|None=None

class UserRegister(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Unique username"
    )

    email: str = Field(
        min_length=5,
        max_length=255,
        description="User email address"
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="User password"
    )

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)