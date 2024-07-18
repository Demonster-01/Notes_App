from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from sqlalchemy.orm import session, Session
import models
from database import get_db
# from ..dependencies import db_dependency
from typing import Optional, List, Annotated
from schemas import PaperBase
from fastapi import FastAPI, HTTPException, Depends, status, Query, Request, Form, File, UploadFile

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.post("/search", response_class=HTMLResponse, status_code=status.HTTP_200_OK, tags=["resources"])
def search(request: Request,
           semester: str = Form(None),
           paper_type: str = Form(None),
           year: str = Form(None),
           subject: str = Form(None),
           db: Session = Depends(get_db)):
    query = db.query(models.Paper)
    if semester:
        query = query.filter(models.Paper.semester == semester)
    if paper_type:
        query = query.filter(models.Paper.paper_type == paper_type)
    if year:
        query = query.filter(models.Paper.semester == semester)
    if subject:
        query = query.filter(models.Paper.paper_type == paper_type)
    papers = query.all()
    if not papers:
        return templates.TemplateResponse("index.html",
                                          {"request": request, "papers": [], "message": "No results found"})

    return templates.TemplateResponse("index.html", {"request": request, "papers": papers})
