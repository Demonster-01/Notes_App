from enum import Enum

from pydantic import BaseModel, EmailStr
from typing import Annotated, Optional, List
from fastapi import Form, UploadFile


class Image(BaseModel):
    filename: Optional[str]
    content_type: Optional[str]

    class Config:
        orm_mode = True

#####----- schema for resources like notes, question..
class PaperBase(BaseModel):
    year: Annotated[Optional[int], Form()] = None
    subject: Annotated[Optional[str], Form()] = None
    # subject: str = Form(...)
    semester:  Annotated[Optional[str], Form()] = None
    paper_type:  Annotated[Optional[str], Form()] = None
    chapter: Annotated[Optional[str], Form()] = None

    class Config:
        orm_mode = True

class PaperUpdate(BaseModel):
    semester: Optional[str] = None
    paper_type: Optional[str] = None
    year: Optional[int] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None


#####----- schema for Users like login and token
class Register(BaseModel):
    FullName: str = Form(...)
    username: str = Form(...)
    Email: str = Form(...)
    password: str = Form(...)
    confirm_password: str = Form(...)
    image: Image | None = None

    class Config:
        orm_mode = True


class UserRole(str, Enum):
    admin = "admin"
    Client = "Client"
    Manager = "Manager"

class UserInDB(BaseModel):
    FullName: str
    username: str
    Email: EmailStr
    password: str
    role: UserRole


class UserOut(BaseModel):
    id: int
    FullName: str
    Username: str
    Email: str

    class Config:
        orm_mode = True


class LoginIn(BaseModel):
    username: str
    password: str



class LoginOut(BaseModel):
    id: int
    username: str
    FullName: str | None = None
    access_token: str

# class LoginOut(BaseModel):
#     access_token: str

class UserProfileUpdate(BaseModel):
    FullName: Optional[str] = None
    Username: Optional[str] = None
    Email: Optional[EmailStr] = None

    class Config:
        orm_mode = True


#####----- schema for Faculty
class FacultyBase(BaseModel):
    Name:str
    Acronym:str


#####----- schema for JWT


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None


#####----- schema for subject
class SubjectBase(BaseModel):
    id: int
    name: str
    faculty_id:int
    subject_code:str

class FacultySchema(BaseModel):
    id: int
    Fullname: str
    Acronym: str
    subjects: List[SubjectBase] = []

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    faculty_id: Optional[int] = None
    subject_code: Optional[str] = None

    class Config:
        orm_mode = True