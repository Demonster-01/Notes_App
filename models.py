from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
from database import Base

class UserRegister(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    FullName = Column(String(30))
    username = Column(String(10), unique=True)
    Email = Column(String(20), unique=True)
    password = Column(String(30))
    confirm_password = Column(String(30))
    role = Column(Enum("Admin", "Client", "Manager", name="user_roles"), default="Client")


    # Relationships
    questions = relationship("AskQue", back_populates="user")
    answers = relationship("AnswerPost", back_populates="user")

class Faculty(Base):
    __tablename__ = 'faculties'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30))

    subjects = relationship("Subject", back_populates="faculty")

class Syllabus(Base):
    __tablename__ = 'syllabuses'

    id = Column(Integer, primary_key=True, index=True)
    year_range = Column(String(10))
    file = Column(String(30))

class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(20), index=True)
    faculty_id = Column(Integer, ForeignKey('faculties.id'))

    faculty = relationship("Faculty", back_populates="subjects")

class Paper(Base):
    __tablename__ = 'papers'

    id = Column(Integer, primary_key=True, index=True)
    file = Column(String(30))
    year = Column(Integer, index=True,nullable=True)
    subject = Column(String(30))
    chapter= Column(String(30),nullable=True)
    semester = Column(String(30),index=True)
    paper_type = Column(Enum("Syllabus", "Notes","Question","Answer", name="Paper-type"),index=True)



class AskQue(Base):
    __tablename__ = 'ask_que'

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(500))
    question_img = Column(String(30), nullable=True)
    faculty = Column(String(10))
    subject = Column(String(30))
    chapter = Column(String(30), nullable=True)
    semester = Column(String(30), index=True)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship("UserRegister", back_populates="questions")
    answers = relationship("AnswerPost", back_populates="question")

class AnswerPost(Base):
    __tablename__ = 'ans_post'

    id = Column(Integer, primary_key=True, index=True)
    answer = Column(String(500))
    ans_img = Column(String(30), nullable=True)
    question_id = Column(Integer, ForeignKey('ask_que.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    question = relationship("AskQue", back_populates="answers")
    user = relationship("UserRegister", back_populates="answers")