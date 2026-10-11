from fastapi import FastAPI, Depends, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from .database import Base, engine, get_db
from . import models as m
from .schemas import NoteIn, NotePatch, NoteOut, FolderIn, FolderOut, TagIn, TagOut

Base.metadata.create_all(bind=engine)
app = FastAPI(title="DevNotes API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

def load_note(db, note_id):
    note = db.scalar(select(m.Note).options(selectinload(m.Note.tags), selectinload(m.Note.folder)).where(m.Note.id == note_id))
    if not note: raise HTTPException(404, "Note not found")
    return note
def resolve_tags(db, names):
    tags=[]
    for raw in names:
        name=raw.strip()
        if not name or len(name)>40: raise HTTPException(422, "Tag names must contain 1–40 characters")
        tag=db.scalar(select(m.Tag).where(m.Tag.name == name))
        if not tag: tag=m.Tag(name=name); db.add(tag); db.flush()
        if tag not in tags: tags.append(tag)
    return tags
@app.get("/api/health")
def health(): return {"status":"ok"}
@app.get("/api/notes", response_model=list[NoteOut])
def list_notes(q: str = "", folder_id: int | None = None, tag: str | None = None, pinned: bool | None = None, archived: bool = False, sort: str = "updated", limit: int = Query(100, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    stmt=select(m.Note).options(selectinload(m.Note.tags), selectinload(m.Note.folder)).where(m.Note.archived == archived)
    if q.strip():
        needle=f"%{q.strip()}%"; stmt=stmt.where(or_(m.Note.title.ilike(needle), m.Note.content.ilike(needle)))
    if folder_id is not None: stmt=stmt.where(m.Note.folder_id == folder_id)
    if tag: stmt=stmt.join(m.Note.tags).where(m.Tag.name == tag)
    if pinned is not None: stmt=stmt.where(m.Note.pinned == pinned)
    stmt=stmt.order_by(m.Note.title.asc() if sort == "title" else m.Note.updated_at.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).unique().all()
@app.post("/api/notes", response_model=NoteOut, status_code=201)
def create_note(data: NoteIn, db: Session = Depends(get_db)):
    if data.folder_id and not db.get(m.Folder, data.folder_id): raise HTTPException(404,"Folder not found")
    note=m.Note(title=data.title.strip(), content=data.content, folder_id=data.folder_id, pinned=data.pinned, archived=data.archived, tags=resolve_tags(db,data.tags))
    db.add(note); db.commit(); return load_note(db,note.id)
@app.get("/api/notes/{note_id}", response_model=NoteOut)
def get_note(note_id:int, db:Session=Depends(get_db)): return load_note(db,note_id)
@app.patch("/api/notes/{note_id}", response_model=NoteOut)
def update_note(note_id:int, data:NotePatch, db:Session=Depends(get_db)):
    note=load_note(db,note_id); values=data.model_dump(exclude_unset=True)
    if "folder_id" in values and values["folder_id"] is not None and not db.get(m.Folder,values["folder_id"]): raise HTTPException(404,"Folder not found")
    if "tags" in values: note.tags=resolve_tags(db,values.pop("tags") or [])
    for key,value in values.items(): setattr(note,key,value.strip() if key=="title" else value)
    db.commit(); return load_note(db,note_id)
@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id:int, db:Session=Depends(get_db)):
    note=load_note(db,note_id); db.delete(note); db.commit(); return Response(status_code=204)
@app.get("/api/folders", response_model=list[FolderOut])
def folders(db:Session=Depends(get_db)): return db.scalars(select(m.Folder).order_by(m.Folder.name)).all()
@app.post("/api/folders", response_model=FolderOut, status_code=201)
def create_folder(data:FolderIn, db:Session=Depends(get_db)):
    folder=m.Folder(name=data.name.strip()); db.add(folder)
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(409,"Folder already exists")
    db.refresh(folder); return folder
@app.patch("/api/folders/{folder_id}", response_model=FolderOut)
def rename_folder(folder_id:int,data:FolderIn,db:Session=Depends(get_db)):
    folder=db.get(m.Folder,folder_id)
    if not folder: raise HTTPException(404,"Folder not found")
    folder.name=data.name.strip()
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(409,"Folder already exists")
    db.refresh(folder); return folder
@app.delete("/api/folders/{folder_id}",status_code=204)
def delete_folder(folder_id:int,db:Session=Depends(get_db)):
    folder=db.get(m.Folder,folder_id)
    if not folder: raise HTTPException(404,"Folder not found")
    db.delete(folder); db.commit(); return Response(status_code=204)
@app.get("/api/tags",response_model=list[TagOut])
def tags(db:Session=Depends(get_db)): return db.scalars(select(m.Tag).order_by(m.Tag.name)).all()
@app.post("/api/tags",response_model=TagOut,status_code=201)
def create_tag(data:TagIn,db:Session=Depends(get_db)):
    tag=m.Tag(name=data.name.strip()); db.add(tag)
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(409,"Tag already exists")
    db.refresh(tag); return tag
@app.delete("/api/tags/{tag_id}",status_code=204)
def delete_tag(tag_id:int,db:Session=Depends(get_db)):
    tag=db.get(m.Tag,tag_id)
    if not tag: raise HTTPException(404,"Tag not found")
    db.delete(tag); db.commit(); return Response(status_code=204)
