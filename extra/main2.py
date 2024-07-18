from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, status, Query, Request, Form, File, UploadFile
from pydantic import BaseModel, EmailStr
from typing import Annotated, Optional, List
import models

from passlib.context import CryptContext
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import Paper, UserRegister
from database import engine, get_db, Base, SessionLocal
from sqlalchemy.orm import session, Session
from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")


# Example secret key for demonstration purposes (should be securely stored)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Adjust as needed
# Simulated database model for demonstration
class User:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role
fake_users_db = {
    "admin": User(username="admin", role="Admin"),
    "user": User(username="user", role="Client"),
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hash context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = {"sub": username}
    except JWTError:
        raise credentials_exception
    return token_data

def admin_required(current_user: models.UserRegister = Depends(get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


class Image(BaseModel):
    filename: Optional[str]
    content_type: Optional[str]

    class Config:
        orm_mode = True


class PaperBase(BaseModel):
    images: Optional[List[UploadFile]] = None
    year: Annotated[Optional[str], Form()] = None
    subject: str = Form(...)
    semester: str = Form(...)
    paper_type: str = Form(...)

    class Config:
        orm_mode = True

class Register(BaseModel):
    FullName: str = Form(...)
    username: str = Form(...)
    Email: str = Form(...)
    password: str = Form(...)
    confirm_password: str = Form(...)
    image: Image | None = None

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    FullName: str
    username: str
    Email: EmailStr
    password: str


class UserOut(BaseModel):
    FullName: str
    username: str
    Email: EmailStr



class LoginIn(BaseModel):
    username: str
    password: str

class LoginOut(BaseModel):
    username: str
    Email: EmailStr
    FullName: str | None = None



# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#

db_dependency = Annotated[session, Depends(get_db)]



@app.post("/post/", status_code=status.HTTP_201_CREATED,
tags=["resources"])
async def create_paper(
    year: int = Form(...),
    subject: str = Form(...),
    semester: str = Form(...),
    paper_type: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
current_user: dict = Depends(get_current_user)
):
    try:
        # Check if current_user is admin
        if current_user["sub"] != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

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



@app.post("/papers", response_model=List[PaperBase], status_code=status.HTTP_200_OK,tags=["resources"])
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


@app.post("/search", response_class=HTMLResponse, status_code=status.HTTP_200_OK,tags=["resources"])
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)



@app.post("/register/", status_code=status.HTTP_201_CREATED, response_model=UserOut,tags=["users"])
async def register(
        request: Request,
        FullName: str = Form(...),
        username: str = Form(...),
        Email: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        db: Session = Depends(get_db)
):
    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    existing_user = db.query(models.UserRegister).filter(
        (models.UserRegister.username == username) | (models.UserRegister.Email == Email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or Email already exists")

    hashed_password = get_password_hash(password)

    new_user = models.UserRegister(
        FullName=FullName,
        username=username,
        Email=Email,
        password=hashed_password  # Store hashed password
        # password=password

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserOut(
        FullName=new_user.FullName,
        username=new_user.username,
        Email=new_user.Email
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/login/", response_model=LoginOut,tags=["users"])
async def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(models.UserRegister).filter(models.UserRegister.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    # if user.password != password:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")

    return LoginOut(
        username=user.username,
        Email=user.Email,
        FullName=user.FullName
    )





@app.post("/ask_question/", status_code=status.HTTP_201_CREATED,tags=["question"])
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


@app.post("/post_answer/", status_code=status.HTTP_201_CREATED,tags=["question"])
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


@app.get("/subject/{subject_id}", response_model=Optional[PaperBase],tags=["question"])
def get_subject_by_id(subject_id: int):
    for subject in PaperBase:
        if subject.id == subject_id:
            return subject
    raise HTTPException(status_code=404, detail="Subject not found")


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}



# Example product database
fake_products_db = [
    {"product_name": "Laptop", "category": "Electronics"},
    {"product_name": "Phone", "category": "Electronics"},
    {"product_name": "Shoes", "category": "Fashion"},
    # ... more products
]

# Model for the product
class Product(BaseModel):
    product_name: str
    category: str

class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 10):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/products/", response_model=list[Product])
async def read_products(commons: Annotated[CommonQueryParams, Depends()]):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
        products = [item for item in fake_products_db if commons.q.lower() in item["product_name"].lower()]
    else:
        products = fake_products_db

    items = products[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response

def common_parameters(q: str = None, skip: int = 0, limit: int = 10):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons
