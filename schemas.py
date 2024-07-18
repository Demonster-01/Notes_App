from pydantic import BaseModel, EmailStr
from typing import Annotated, Optional, List
from fastapi import Form, UploadFile


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
