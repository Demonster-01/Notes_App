from fastapi import APIRouter, Depends, HTTPException,Form,status,UploadFile,File
from sqlalchemy.orm import Session
from database import get_db
import models
from typing import  Optional, List,Annotated
from schemas import PaperBase
from models import Paper

router = APIRouter()



@router.post("/post/", status_code=status.HTTP_201_CREATED,
tags=["resources"])
async def create_paper(
    year: int = Form(...),
    subject: str = Form(...),
    semester: str = Form(...),
    paper_type: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    try:
        db_paper = models.Paper(
            file=images[0].filename if images else None,  # Store the first image's filename or None
            year=year,
            subject=subject,
            semester=semester,
            paper_type=paper_type
        )
        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)

        # Handle file upload if an image is provided
        if images:
            for image in images:
                file_location = f"uploads/{image.filename}"
                with open(file_location, "wb") as file:
                    file.write(image.file.read())
        return db_paper
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/papers", response_model=List[PaperBase], status_code=status.HTTP_200_OK,tags=["resources"])
async def get_papers_by_semester_type(
        semester: Annotated[Optional[str], Form()] = None,
        paper_type: Annotated[Optional[str], Form()] = None,
        year: Annotated[Optional[str], Form()] = None,
        subject: Annotated[Optional[str], Form()] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Paper)

    if semester:
        query = query.filter(Paper.semester == semester)
    if paper_type:
        query = query.filter(Paper.paper_type == paper_type)
    if semester:
        query = query.filter(Paper.year == year)
    if paper_type:
        query = query.filter(Paper.subject == subject)

    papers = query.all()
    if not papers:
        raise HTTPException(status_code=404, detail="Data not found")

    return papers