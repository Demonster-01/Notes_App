from fastapi import FastAPI, Request, UploadFile, File, Depends, Form, Query,status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from starlette.exceptions import HTTPException

from database import get_db
from models import Paper

app = FastAPI()
templates = Jinja2Templates(directory="templates")

from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})


@app.post("/post/", status_code=status.HTTP_201_CREATED, tags=["admins"])
async def create_paper(
        # year: Optional[str] = Query(None, description="The year of the paper"),
        # subject: Optional[str] = Query(None, description="The subject of the paper"),
        # semester: Optional[str] = Query(None, description="The semester of the paper"),
        # paper_type: Optional[str] = Query(None, description="The paper type of the paper"),
        # chapter: Optional[str] = Query(None, description="The chapter of the paper"),
        # image: Optional[UploadFile] = File(None),
        year: Optional[str] = Form(None, description="The year of the paper"),
        subject: Optional[str] = Form(None, description="The subject of the paper"),
        semester: Optional[str] = Form(None, description="The semester of the paper"),
        paper_type: Optional[str] = Form(None, description="The paper type of the paper"),
        chapter: Optional[str] = Form(None, description="The chapter of the paper"),
        image: Optional[List[UploadFile]] = File(None),
        db: Session = Depends(get_db)
):
    try:
        if image:
            file_location = f"uploads/{image.filename}"
            with open(file_location, "wb") as file:
                file.write(image.file.read())
        else:
            file_location = None

        db_paper = Paper(
            file=image.filename if image else None,
            year=year,
            subject=subject,
            chapter=chapter,
            semester=semester,
            paper_type=paper_type
        )
        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)

        return {"id": db_paper.id, "year": year, "subject": subject, "semester": semester, "paper_type": paper_type,
                "chapter": chapter, "file_location": file_location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit/")
async def submit_form(item: str = Form(...), price: int = Form(...), qty: int = Form(...)):
    # Construct the URL with query parameters
    url = f"/details?item={item}&price={price}&qty={qty}"
    return url