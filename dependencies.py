from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import session, Session
from database import engine, get_db


db_dependency = Annotated[session, Depends(get_db)]
