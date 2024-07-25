from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Form, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models
from Auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from extra.JWTEx import Token
from database import get_db
from schemas import UserOut, Register, UserProfileUpdate, LoginOut

router = APIRouter()


@router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=UserOut, tags=["users"])
async def register(
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

    new_user = models.UserRegister(
        FullName=FullName,
        username=username,
        Email=Email,
        password=password  # Save plain text password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserOut(
        id=new_user.id,
        FullName=new_user.FullName,
        username=new_user.username,
        Email=new_user.Email
    )



@router.post("/token", response_model=LoginOut, tags=["users"])
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








@router.put("/update-profile/{user_id}", response_model=UserOut, tags=["users"])
async def update_profile(
    user_id: int,
    profile: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(Register).filter(Register.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update user details
    if profile.FullName:
        user.FullName = profile.FullName
    if profile.username:
        user.username = profile.username
    if profile.Email:
        user.Email = profile.Email

    # Handle password update
    if profile.password:
        if profile.password != profile.confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
        # user.password = get_password_hash(profile.password)

    db.commit()
    db.refresh(user)

    return UserOut(
        id=user.id,
        FullName=user.FullName,
        username=user.username,
        Email=user.Email
    )