from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class FolderIn(BaseModel): name: str = Field(min_length=1, max_length=80)
class FolderOut(FolderIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
class TagIn(BaseModel): name: str = Field(min_length=1, max_length=40)
class TagOut(TagIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
class NoteIn(BaseModel):
    title: str = Field(default="Untitled note", min_length=1, max_length=200)
    content: str = Field(default="", max_length=500_000)
    folder_id: int | None = None
    tags: list[str] = Field(default_factory=list, max_length=30)
    pinned: bool = False
    archived: bool = False
class NotePatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=500_000)
    folder_id: int | None = None
    tags: list[str] | None = Field(default=None, max_length=30)
    pinned: bool | None = None
    archived: bool | None = None
class NoteOut(BaseModel):
    id: int; title: str; content: str; folder_id: int | None; pinned: bool; archived: bool
    created_at: datetime; updated_at: datetime; tags: list[TagOut] = []; folder: FolderOut | None = None
    model_config = ConfigDict(from_attributes=True)
