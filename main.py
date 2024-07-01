from __future__ import annotations

from fastapi import FastAPI, HTTPException, Depends, status, Query, Request, Form
from pydantic import BaseModel
from typing import Annotated, Optional, List
import models

from passlib.context import CryptContext
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import Paper, UserRegister
from database import engine, get_db, Base, SessionLocal
from sqlalchemy.orm import session, Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


class PaperBase(BaseModel):
    file: str
    year: int
    subject: str
    semester: str
    paper_type: str

    class Config:
        orm_mode = True


class Register(BaseModel):
    FullName: str
    username: str
    Email: str
    password: str
    confirm_password: str

    class Config:
        orm_mode = True


test = {
    1: {
        "name": "ram",
        "faculty": "BBA",
        "subject": "Math"

    }
}

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#

db_dependency = Annotated[session, Depends(get_db)]


@app.post("/post/", status_code=status.HTTP_201_CREATED)
async def create_paper(post: PaperBase, db: Session = Depends(get_db)):
    try:
        db_paper = models.Paper(**post.dict())
        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)
        return db_paper
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/papers", response_model=List[PaperBase], status_code=status.HTTP_200_OK)
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


# {
#   "file": "2021questoin",s
#   "year": "2021",
#   "subject": "math",
#   "semester": "second",
#   "paper_type": "question"
# }


@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/search", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def search(request: Request,
           semester: str = Form(None),
           paper_type: str = Form(None),
           db: Session = Depends(get_db)):
    query = db.query(models.Paper)
    if semester:
        query = query.filter(models.Paper.semester == semester)
    if paper_type:
        query = query.filter(models.Paper.paper_type == paper_type)
    papers = query.all()
    if not papers:
        return templates.TemplateResponse("index.html",
                                          {"request": request, "papers": [], "message": "No results found"})

    return templates.TemplateResponse("index.html", {"request": request, "papers": papers})


# @app.post("/register/")
# async def register(post: Register ,db: Session = Depends(get_db)):
#     try:
#         db_register = models.UserRegister(**post.dict())
#         db.add(db_register)
#         db.commit()
#         db.refresh(db_register)
#         return db_register
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(request: Request,
                   FullName: str = Form(...),
                   username: str = Form(...),
                   Email: str = Form(...),
                   password: str = Form(...),
                   confirm_password: str = Form(...),
                   db: Session = Depends(get_db)):
    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    existing_user = db.query(models.UserRegister).filter(
        (models.UserRegister.username == username) | (models.UserRegister.Email == Email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or Email already exists")
    new_user = models.UserRegister(
        FullName=FullName,
        username=username,
        Email=Email,
        password=password,
        confirm_password=confirm_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request,
                username: str = Form(...),
                password: str = Form(...),
                db: Session = Depends(get_db)):

    print("password:",password)

    user = db.query(models.UserRegister).filter(models.UserRegister.username == username).first()
    print("password:", user)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    if user.password != password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")


    # if not pwd_context.verify(password, user.password):
    #     print("password:", password)
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    return {"message": "Login successful", "user": user.username}


@app.post("/ask_question/", status_code=status.HTTP_201_CREATED)
async def ask_question(request: Request,
                       question: str = Form(...),
                       question_img: str = Form(None),
                       faculty: str = Form(...),
                       subject: str = Form(...),
                       chapter: str = Form(None),
                       semester: str = Form(...),
                       user_id: int = Form(...),
                       db: Session = Depends(get_db)):

    new_question = models.AskQue(
        question=question,
        question_img=question_img,
        faculty=faculty,
        subject=subject,
        chapter=chapter,
        semester=semester,
        user_id=user_id
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@app.post("/post_answer/", status_code=status.HTTP_201_CREATED)
async def post_answer(request: Request,
                      answer: str = Form(...),
                      ans_img: str = Form(None),
                      question_id: int = Form(...),
                      user_id: int = Form(...),
                      db: Session = Depends(get_db)):

    new_answer = models.AnswerPost(
        answer=answer,
        ans_img=ans_img,
        question_id=question_id,
        user_id=user_id
    )
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    return new_answer