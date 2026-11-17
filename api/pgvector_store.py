import math
from datetime import datetime, timezone

import numpy as np
from sqlalchemy import select

from api.database import SessionLocal

from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

PgVectorBase = declarative_base()


class DocumentChunk(PgVectorBase):
    __tablename__ = "document_chunks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    page = Column(Integer, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

def store_chunks(
    document_id: str,
    user_id: str,
    embedded_chunks: list[dict]
) -> int:

    if not document_id or not user_id:
        raise ValueError("Document ID and user ID are required.")

    if not embedded_chunks:
        return 0

    records = []

    for index, chunk in enumerate(embedded_chunks):

        text = chunk.get("text")
        source = chunk.get("source")
        page = chunk.get("page")
        embedding = chunk.get("embedding")

        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Invalid text in chunk {index}")

        if not isinstance(source, str) or not source.strip():
            raise ValueError(f"Invalid source in chunk {index}")

        if not isinstance(page, int) or page < 1:
            raise ValueError(f"Invalid page in chunk {index}")

        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()

        if not isinstance(embedding, (list, tuple)):
            raise ValueError(f"Invalid embedding in chunk {index}")

        if len(embedding) != 384:
            raise ValueError(f"Chunk {index} must have 384 dimensions")

        embedding = [float(value) for value in embedding]

        if not all(math.isfinite(value) for value in embedding):
            raise ValueError(f"Non-finite embedding in chunk {index}")

        records.append(
            DocumentChunk(
                document_id=document_id,
                user_id=user_id,
                chunk_index=index,
                content=text,
                source=source,
                page=page,
                embedding=embedding,
                metadata_=chunk.get("metadata"),
                created_at=datetime.now(timezone.utc)
            )
        )

    db = SessionLocal()

    try:
        db.add_all(records)
        db.commit()

        return len(records)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def search_chunks(
    question_embedding,
    user_id: str,
    top_k: int = 3,
    document_id: str | None = None
) -> list[dict]:

    if not user_id:
        raise ValueError("User ID is required.")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
        raise ValueError("top_k must be a positive integer.")

    if hasattr(question_embedding, "tolist"):
        question_embedding = question_embedding.tolist()

    if not isinstance(question_embedding, (list, tuple)):
        raise ValueError("Question embedding must be a list or array.")

    if len(question_embedding) != 384:
        raise ValueError("Question embedding must have 384 dimensions.")

    question_embedding = [float(value) for value in question_embedding]

    if not all(math.isfinite(value) for value in question_embedding):
        raise ValueError("Question embedding contains invalid values.")

    distance = DocumentChunk.embedding.cosine_distance(
        question_embedding
    ).label("distance")

    statement = (
        select(DocumentChunk, distance)
        .where(DocumentChunk.user_id == user_id)
        .order_by(distance)
        .limit(top_k)
    )

    if document_id is not None:
        statement = statement.where(
            DocumentChunk.document_id == document_id
        )

    db = SessionLocal()

    try:
        rows = db.execute(statement).all()

        results = []

        for chunk, cosine_distance in rows:
            results.append({
                "text": chunk.content,
                "source": chunk.source,
                "page": chunk.page,
                "distance": float(cosine_distance)
            })

        return results

    finally:
        db.close()


def delete_document_chunks(
    document_id: str,
    user_id: str
) -> int:

    if not document_id or not user_id:
        raise ValueError("Document ID and user ID are required.")

    db = SessionLocal()

    try:
        deleted_count = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.user_id == user_id
            )
            .delete(synchronize_session=False)
        )

        db.commit()

        return deleted_count

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()