# backend/app/routes/notes.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.app.utils.database import SessionLocal, Note
from sqlalchemy.orm import Session

# Create a router for note-related endpoints
router = APIRouter(prefix="/api/notes", tags=["notes"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for creating/updating notes
class NoteCreateRequest(BaseModel):
    title: str
    content: str
    subject: str
    tags: Optional[List[str]] = None
    user_id: int

class NoteUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    subject: Optional[str] = None
    tags: Optional[List[str]] = None

# Create a new note
@router.post("/")
def create_note(request: NoteCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new note.
    """
    try:
        note = Note(
            title=request.title,
            content=request.content,
            subject=request.subject,
            tags=",".join(request.tags) if request.tags else None,
            user_id=request.user_id,  # Ensure this line is present
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return {"message": "Note created successfully", "note_id": note.id}  # Ensure this line returns the note_id
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve all notes
@router.get("/")
def get_notes(db: Session = Depends(get_db)):
    """
    Retrieve all notes.
    """
    notes = db.query(Note).all()
    return notes

# Retrieve notes by subject
@router.get("/subject/{subject}")
def get_notes_by_subject(subject: str, db: Session = Depends(get_db)):
    """
    Retrieve notes by subject.
    """
    notes = db.query(Note).filter(Note.subject == subject).all()
    return notes

# Retrieve notes by tag
@router.get("/tag/{tag}")
def get_notes_by_tag(tag: str, db: Session = Depends(get_db)):
    """
    Retrieve notes by tag.
    """
    notes = db.query(Note).filter(Note.tags.contains(tag)).all()
    return notes

# Update a note
@router.put("/{note_id}")
def update_note(note_id: int, request: NoteUpdateRequest, db: Session = Depends(get_db)):
    """
    Update an existing note.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        if request.title:
            note.title = request.title
        if request.content:
            note.content = request.content
        if request.subject:
            note.subject = request.subject
        if request.tags:
            note.tags = ",".join(request.tags)
        db.commit()
        db.refresh(note)
        return note
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Delete a note
@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """
    Delete a note.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        db.delete(note)
        db.commit()
        return {"detail": "Note deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))