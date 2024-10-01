from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from sqlalchemy.orm import Session
from typing import Optional, List
import models
from database import get_db
from dependencies import get_current_user
from schemas import PaperBase, User

router = APIRouter()


@router.post("/ask_question/", status_code=status.HTTP_201_CREATED, tags=["question"])
async def ask_question(
                       question: str = Form(...),
                       question_img: str = Form(None),
                       faculty: str = Form(...),
                       subject: str = Form(...),
                       chapter: str = Form(None),
                       semester: str = Form(...),
                       db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    new_question = models.AskQue(
        question=question,
        question_img=question_img,
        faculty=faculty,
        subject=subject,
        chapter=chapter,
        semester=semester,
        user_id=current_user.id,  # Use the logged-in user's ID
        timestamp=datetime.now(timezone.utc)  # Add the current timestamp
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question


@router.post("/post_answer/", status_code=status.HTTP_201_CREATED, tags=["question"])
async def post_answer(
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


@router.get("/subject/{subject_id}", response_model=Optional[PaperBase], tags=["question"])
async def get_subject_by_id(subject_id: int):
    for subject in PaperBase:
        if subject.id == subject_id:
            return subject
    raise HTTPException(status_code=404, detail="Subject not found")
