from datetime import timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException,Form,status,UploadFile,File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from Auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from database import get_db

import models
from typing import  Optional, List,Annotated

from dependencies import admin_required
from schemas import PaperBase, LoginIn, LoginOut, TokenData, Token
from models import Paper

router = APIRouter()

@router.post("/post/{id}", status_code=status.HTTP_201_CREATED, tags=["admins"])
async def create_paper(
    year: int = Form(...),
    subject: str = Form(...),
    semester: str = Form(...),
    paper_type: str = Form(...),
    chapter: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    try:
        # Ensure images is a list and process accordingly
        if images:
            file_names = [image.filename for image in images]
        else:
            file_names = None

        db_paper = Paper(
            file=images[0].filename if images else None,  # Store the first image's filename or None
            year=year,
            subject=subject,
            chapter=chapter,
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



@router.post("/papers/{year}", response_model=List[PaperBase], status_code=status.HTTP_200_OK,tags=["admins"])
async def get_papers_by(
        semester: Annotated[Optional[str], Form()] = None,
        paper_type: Annotated[Optional[str], Form()] = None,
        year= int,
        subject: Annotated[Optional[str], Form()] = None,
        chapter: Annotated[Optional[str], Form()] = None,
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
    if chapter:
        query = query.filter(Paper.chapter == chapter)

    papers = query.all()
    if not papers:
        raise HTTPException(status_code=404, detail="Data not found")

    return papers



@router.post("/faculty/", tags=["admins"])
async def create_faculty(
        name: str = Form(...),
        db: Session = Depends(get_db),
        current_user: models.UserRegister = Depends(admin_required)
):
    new_faculty = models.Faculty(
        name=name
    )
    db.add(new_faculty)
    db.commit()
    db.refresh(new_faculty)

    return new_faculty




@router.post("/token", response_model=LoginOut, tags=["admins"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.UserRegister).filter(models.UserRegister.username == form_data.username).first()
    print("models.UserRegister.username",models.UserRegister.username,"form_data.username",form_data.username)
    if not user or not user.password == form_data.password:  # No password hashing for testing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return LoginOut(
        id=user.id,
        username=user.username,
        FullName=user.FullName,
        access_token=access_token
    )

