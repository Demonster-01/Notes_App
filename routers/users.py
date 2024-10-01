from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Form, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session
import models
from Auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from dependencies import get_current_user
from models import UserRegister
from database import get_db
from schemas import UserOut, Register, UserProfileUpdate, LoginOut

router = APIRouter()


@router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=UserOut, tags=["users"])
async def register(
        FullName: str = Query(...),
        username: str = Query(...),
        Email: EmailStr =  Query(...),
        password: str =  Query(...),
        confirm_password: str =  Query(...),
        db: Session = Depends(get_db)
):
    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    existing_user = db.query(models.UserRegister).filter(
        (models.UserRegister.Username == username) | (models.UserRegister.Email == Email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or Email already exists")

    new_user = models.UserRegister(
        FullName=FullName,
        Username=username,
        Email=Email,
        password=password  # Save plain text password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserOut(
        id=new_user.id,
        FullName=new_user.FullName,
        Username=new_user.Username,
        Email=new_user.Email
    )



@router.post("/token", response_model=LoginOut, tags=["users"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserRegister).filter(UserRegister.Username == form_data.username).first()
    # print("models.UserRegister.username",UserRegister.username,"form_data.username",form_data.username)
    if not user or not user.password == form_data.password:  # No password hashing for testing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.Username}, expires_delta=access_token_expires
    )
    return LoginOut(
        id=user.id,
        username=user.Username,
        FullName=user.FullName,
        access_token=access_token
    )


@router.put("/update-profile",response_model=UserOut,status_code=status.HTTP_200_OK,tags=["users"])
def update_profile(
        # profile_update: UserProfileUpdate,
        FullName:Optional[str] = Query(None, description="Yor FullName"),
        Username:Optional[str] = Query(None, description="Yor username"),
        current_user: UserRegister = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_id = current_user.id
    user = db.query(UserRegister).filter(UserRegister.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields if provided
    if FullName:
        user.FullName = FullName
    if Username:
        user.Username = Username

    db.commit()
    db.refresh(user)

    return UserOut(
        id=user.id,
        FullName=user.FullName,
        Username=user.Username,
        Email=user.Email
    )