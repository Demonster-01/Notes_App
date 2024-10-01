from datetime import timedelta
import aiofiles
import logging
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query, Path, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional, List

from Auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from database import get_db
from models import Paper, Faculty, UserRegister, Subject
from schemas import PaperBase, LoginIn, LoginOut, TokenData, Token, FacultyBase, SubjectBase, FacultySchema, SubjectUpdate
from dependencies import admin_required

router = APIRouter()
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


def get_paper_by_id(db: Session, paper_id: int):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper
########----manage resources

@router.post("/post/{id}", status_code=status.HTTP_201_CREATED, tags=["admins"])
async def create_paper(
        year: int = Form(...),
        subject: str = Form(...),
        semester: str = Form(...),
        paper_type: str = Form(...),
        chapter: str = Form(...),
        images: Optional[List[UploadFile]] = File(None),
        db: Session = Depends(get_db),
        current_user: UserRegister = Depends(admin_required)
):
    logger.info(f"User {current_user.username} is creating a paper for {subject}, semester {semester}")
    try:
        file_names = [image.filename for image in images] if images else None

        db_paper = Paper(
            file=images[0].filename if images else None,
            year=year,
            subject=subject,
            chapter=chapter,
            semester=semester,
            paper_type=paper_type
        )
        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)

        if images:
            for image in images:
                file_location = f"uploads/{image.filename}"
                async with aiofiles.open(file_location, 'wb') as out_file:
                    content = await image.read()
                    await out_file.write(content)

        return db_paper
    except Exception as e:
        logger.error(f"Error occurred while creating paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.put("/update-resources/{paper_id}", response_model=PaperBase, status_code=status.HTTP_200_OK, tags=["admins"])
async def update_paper(
    paper_id: int = Path(..., description="The ID of the paper to update"),
    semester: Optional[str] = Form(None),
    paper_type: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    subject: Optional[str] = Form(None),
    chapter: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: UserRegister = Depends(admin_required),
):
    paper = get_paper_by_id(db, paper_id)

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

@router.delete("/delete-resources/{paper_id}/", tags=["admins"], status_code=status.HTTP_200_OK)
async def delete_resource(
        paper_id: int,
        current_user: UserRegister = Depends(admin_required),
        db: Session = Depends(get_db)
):
    resource = get_paper_by_id(db, paper_id)

    db.delete(resource)
    db.commit()

    return {"detail": "Paper deleted successfully"}

@router.get("/papers/", response_model=List[PaperBase], status_code=status.HTTP_200_OK, tags=["admins"])
async def get_papers(
        semester: Optional[str] = Query(None, description="The paper of the which semester"),
        paper_type: Optional[str] = Query(None, description="The Type of the paper:Note,Question,Answer"),
        year: Optional[str] = Query(None, description="The year of the paper"),
        subject: Optional[str] = Query(None, description="The subject of the paper"),
        chapter: Optional[str] = Query(None, description="The Chapter of the paper"),
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

########---- login

@router.post("/token", response_model=LoginOut, tags=["admins"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserRegister).filter(UserRegister.username == form_data.username).first()
    print("models.UserRegister.username", UserRegister.username, "form_data.username", form_data.username)
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



########---- faculty

@router.post("/faculty/", tags=["admins"])
async def create_faculty(
        Fullname: str =  Query(...,description="Faculty Full Name"),
        Acronym: str = Query(...,description="Faculty Acronym e,g: BIM,BBA"),
        db: Session = Depends(get_db),
        current_user: UserRegister = Depends(admin_required)
):
    # Check for duplicate faculty
    existing_faculty = db.query(Faculty).filter(
        Faculty.Fullname == Fullname,
        Faculty.Acronym == Acronym
    ).first()

    if existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="faculty already exists ."
        )
    new_faculty = Faculty(
        Fullname=Fullname,
        Acronym=Acronym
    )
    db.add(new_faculty)
    db.commit()
    db.refresh(new_faculty)

    return new_faculty


@router.put("/Update-faculty/{faculty_id}/", tags=["admins"])
async def update_faculty(
        faculty_id: int,
        FullName: Optional[str] = Query(None, description="Faculty FullName"),
        Acronym: Optional[str] = Query(None, description="Faculty Acronym E.g., BIM, BBA"),
        current_user: UserRegister = Depends(admin_required),
        db: Session = Depends(get_db)
):
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()

    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")

    if FullName:
        faculty.Fullname = FullName
    if Acronym:
        faculty.Acronym = Acronym

    db.commit()
    db.refresh(faculty)

    return faculty


@router.delete("/delete-faculty/{faculty_id}/", tags=["admins"], status_code=status.HTTP_200_OK)
async def delete_faculty(
        faculty_id: int,
        current_user: UserRegister = Depends(admin_required),
        db: Session = Depends(get_db)
):
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()

    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")

    db.delete(faculty)
    db.commit()
    return None



########----manage subject
@router.post("/subjects/", status_code=status.HTTP_201_CREATED, tags=["admins"], response_model=SubjectBase)
async def add_subject(name: str = Query(..., description="The subject name you want to add"),
                      subject_code:Optional[str] = Query(None, description="The code of subject eg: It 200"),
                      faculty_id:Optional[str] = Query(None, description="Faculty of the subject"),
                      current_user: UserRegister = Depends(admin_required),
                      db: Session = Depends(get_db)):

    # Check for duplicate subject
    existing_subject = db.query(Subject).filter(
        Subject.name == name,
        Subject.subject_code == subject_code,
        Subject.faculty_id == faculty_id
    ).first()

    if existing_subject:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="subject Already exist in faculty, can not add duplicate")

    db_subject = Subject(
        name=name,
        subject_code=subject_code,
        faculty_id=faculty_id
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)

    return db_subject


@router.get("/get-subjects/", status_code=status.HTTP_201_CREATED, tags=["admins"], response_model=FacultySchema)
async def get_subject(
        faculty_name: Optional[str] = Query(None, description="Name of faculty to get subject"),
        current_user: UserRegister = Depends(admin_required),
        db: Session = Depends(get_db)
):
    if not faculty_name:
        raise HTTPException(status_code=400, detail="Faculty name is required")
    faculty = db.query(Faculty).filter(Faculty.Fullname == faculty_name).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty

@router.put("/Update-subject/{subject_id}/", response_model=SubjectBase, status_code=status.HTTP_200_OK, tags=["admins"])
async def update_subject(
        subject_id: int,
        name: Optional[str] = Query(None, description="The subject name you want to update"),
        subject_code: Optional[str] = Query(None, description="The code of subject"),
        faculty_id: Optional[str] = Query(None, description="Faculty of the subject"),
        current_user: UserRegister = Depends(admin_required),
        db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()

    if name:
        subject.name = name
    if subject_code:
        subject.subject_code = subject_code
    if faculty_id:
        subject.faculty_id = faculty_id

    db.commit()
    db.refresh(subject)

    return subject


@router.delete("/subjects/{subject_id}/", status_code=status.HTTP_204_NO_CONTENT, tags=["admins"])
async def delete_subject(subject_id: int,
                         current_user: UserRegister = Depends(admin_required),
                         db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    db.delete(subject)
    db.commit()
    return None

    # return {"detail": "Subject deleted successfully"}
