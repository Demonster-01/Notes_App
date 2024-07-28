from __future__ import annotations

import jwt
from fastapi import FastAPI, Depends, Request, HTTPException
from typing import Annotated

from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from starlette import status

from extra.auth import TokenData
from database import engine, get_db
from sqlalchemy.orm import Session

import models
from dependencies import admin_required
from routers import resources, users, qna
from admin import admin
from schemas import User

description = """
NoteAPP API. 🚀😁😁

## Items

You can **Upload your question and ask for an answer**.
You can also get access to old questions, notes, and answers.
"""


tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "resources",
        "description": "Manage resources like questions and notes.",
    },
    {
        "name": "question",
        "description": "Manage user-asked questions and answer logic.",
    },
    {
        "name": "admins",
        "description": "Manage admin functions",
    },
]

app = FastAPI(
    title="NoteApp",
    description=description,
    summary="Student junction for notes, questions",
    version="0.0.1",
    terms_of_service="/",
    openapi_tags=tags_metadata
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # Assuming the user_id is stored under "sub"
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
db_dependency = Annotated[Session, Depends(get_db)]


app.include_router(users.router)
app.include_router(qna.router)
app.include_router(resources.router)
# app.include_router(faculty.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admins"],
    responses={418: {"description": "I'm a teapot"}},
)

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


# @app.get("/admin-data/")
# async def get_admin_data(current_user: User = Depends(admin_required)):
#     return {"message": "This is protected data for admin users only"}
#
# @app.get("/users/me/", response_model=User)
# async def read_admin_data(current_user: models.UserRegister = Depends(admin_required)):
#     return current_user