from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status, Path, Body
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import session, Session
import models
from database import get_db
# from ..dependencies import db_dependency
from typing import Optional, List, Annotated
from schemas import PaperBase,PaperUpdate
from fastapi import FastAPI, HTTPException, Depends, status, Query, Request, Form, File, UploadFile

from models import Paper

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/search/", response_model=List[PaperBase], status_code=status.HTTP_200_OK, tags=["resources"])
async def search(

    semester: Optional[str] = Form(None),
    paper_type: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    subject: Optional[str] = Form(None),
    chapter: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    query = db.query(Paper)
    if semester:
        query = query.filter(Paper.semester == semester)
    if paper_type:
        query = query.filter(Paper.paper_type == paper_type)
    if year:
        query = query.filter(Paper.semester == year)
    if subject:
        query = query.filter(Paper.paper_type == subject)
    if chapter:
        query = query.filter(Paper.chapter == chapter)
    papers = query.all()
    if not papers:
        raise HTTPException(status_code=404, detail="Data not found")

    return papers
    # if not papers:
    #     return templates.TemplateResponse("index.html",
    #                                       {"request": request, "papers": [], "message": "No results found"})
    #
    # return templates.TemplateResponse("index.html", {"request": request, "papers": papers})





@router.put("/papers/{paper_id}", response_model=PaperBase, status_code=status.HTTP_200_OK, tags=["resources"])
async def update_paper(
    paper_id: int = Path(..., description="The ID of the paper to update"),
    semester: Optional[str] = Form(None),
    paper_type: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    subject: Optional[str] = Form(None),
    chapter: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Paper not found")

    if semester is not None:
        paper.semester = semester
    if paper_type is not None:
        paper.paper_type = paper_type
    if year is not None:
        paper.year = year
    if subject is not None:
        paper.subject = subject
    if chapter is not None:
        paper.chapter = chapter

    db.commit()
    db.refresh(paper)

    return paper