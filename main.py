from __future__ import annotations
from fastapi import FastAPI, Depends, Request
from typing import Annotated


from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import engine, get_db, Base, SessionLocal
from sqlalchemy.orm import Session



import models
from routers import resources, users, qna
from admin import admin

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
db_dependency = Annotated[Session, Depends(get_db)]

app.include_router(users.router)
app.include_router(qna.router)
app.include_router(resources.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    # dependencies=[Depends()],
    responses={418: {"description": "I'm a teapot"}},
)

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# @app.post("/register/")
# async def register(post: Register, db: Session = Depends(get_db)):
#     try:
#         db_register = models.UserRegister(**post.dict())
#         db.add(db_register)
#         db.commit()
#         db.refresh(db_register)
#         return db_register
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
