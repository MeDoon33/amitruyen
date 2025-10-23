from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChapterBase(BaseModel):
    chapter_number: float
    title: Optional[str] = None
    image_urls: str

class ChapterCreate(ChapterBase):
    comic_id: int

class ChapterResponse(ChapterBase):
    id: int
    comic_id: int
    created_at: datetime
    views: int

    class Config:
        from_attributes = True

class ComicBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: Optional[str] = None
    description: Optional[str] = None
    cover_image: str
    genre: Optional[str] = None
    status: str = 'ongoing'
    tags: Optional[str] = None

class ComicCreate(ComicBase):
    pass

class ComicResponse(ComicBase):
    id: int
    created_at: datetime
    updated_at: datetime
    views: int
    rating: float
    chapters: List[ChapterResponse]

    class Config:
        from_attributes = True