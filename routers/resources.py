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

    semester: Optional[str] = Query(None, description="Semester"),
    paper_type: Optional[str] = Query(None, description="Type of paper"),
    year: Optional[int] = Query(None, description="Year"),
    subject: Optional[str] = Query(None, description="Subject"),
    chapter: Optional[str] = Query(None, description="Chapter"),
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




