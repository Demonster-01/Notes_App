from typing import Annotated

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

import schemas
from Auth import SECRET_KEY, ALGORITHM, get_user
from database import get_db
from extra.auth import verify_token, TokenData
from models import UserRegister

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




# async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
#     credential_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         # Print header and payload without verification
#         header = jwt.get_unverified_header(token)
#         payload = jwt.get_unverified_claims(token)
#         print(f"JWT Header: {header}")
#         print(f"JWT Payload: {payload}")
#
#         # Decode the token to validate the signature
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credential_exception
#         user = db.query(UserRegister).filter(UserRegister.username == username).first()
#         if user is None:
#             raise credential_exception
#     except JWTError:
#         raise credential_exception
#
#     return user





async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(UserRegister).filter(UserRegister.Username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


async def admin_required(current_user: UserRegister = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user





