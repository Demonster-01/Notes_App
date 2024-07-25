from fastapi import APIRouter, Depends, HTTPException,Form,status,UploadFile,File
from sqlalchemy.orm import Session
from database import get_db
import models
from typing import  Optional, List,Annotated
from schemas import PaperBase
from models import Faculty

router = APIRouter()

@router.post("/faculty/",tags=["admins"])
async def Faculty(
        name: str = Form(...),
        db: Session = Depends(get_db)
):
    new_faculty=models.Faculty(
        name=name
    )
    db.add(new_faculty)
    db.commit()
    db.refresh(new_faculty)
    return new_faculty