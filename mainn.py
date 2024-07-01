from __future__ import annotations

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from models import Paper
from database import engine, get_db, Base

app = FastAPI()
Base.metadata.create_all(bind=engine)


class PaperBase(BaseModel):
    file: str
    year: int
    subject: str
    semester: str
    paper_type: str

    class Config:
        orm_mode = True


@app.get("/papers", response_model=List[PaperBase])
async def get_papers_by_semester_type(semester: Optional[str] = Query(None),
                                      paper_type: Optional[str] = Query(None),
                                      db: Session = Depends(get_db)):
    query = db.query(Paper)

    if semester:
        query = query.filter(Paper.semester == semester)
    if paper_type:
        query = query.filter(Paper.paper_type == paper_type)

    papers = query.all()
    if not papers:
        raise HTTPException(status_code=404, detail="Data not found")

    return papers
