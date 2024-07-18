from fastapi import APIRouter, Depends, HTTPException,Request,Form,status
from sqlalchemy.orm import session, Session
import models
from database import get_db
# from ..dependencies import db_dependency
from typing import  Optional, List
from schemas import UserIn,UserOut,LoginIn,LoginOut


from passlib.context import CryptContext

router = APIRouter()




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=UserOut,tags=["users"])
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


@router.post("/login/", response_model=LoginOut,tags=["users"])
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

