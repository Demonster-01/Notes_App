<<<<<<< HEAD
import enum
=======
>>>>>>> origin/try
from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from database import Base


# Enum for user roles
class UserRole(enum.Enum):
    admin = "admin"
    client = "Client"
    manager = "Manager"

# Enum for paper types
class PaperType(enum.Enum):
    syllabus = "Syllabus"
    notes = "Notes"
    question = "Question"
    answer = "Answer"

class UserRegister(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.client)
    # role = Column(Enum("admin", "Client", "Manager", name="user_roles"), default="Client")
=======
    FullName = Column(String(30))
    Username = Column(String(10), unique=True)
    Email = Column(String(20), unique=True)
    password = Column(String(30))
    role = Column(Enum("admin", "Client", "Manager", name="user_roles"), default="Client")
>>>>>>> origin/try


    # Relationships
    questions = relationship("AskQue", back_populates="user", cascade="all, delete-orphan")
    answers = relationship("AnswerPost", back_populates="user", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Faculty(Base):
    __tablename__ = 'faculties'

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    full_name = Column(String(100), nullable=False)
    acronym = Column(String(30), nullable=False)
=======
    Fullname = Column(String(30))
    Acronym = Column(String(30))
>>>>>>> origin/try

    subjects = relationship("Subject", back_populates="faculty", cascade="all, delete-orphan")

class Syllabus(Base):
    __tablename__ = 'syllabuses'

    id = Column(Integer, primary_key=True, index=True)
    year_range = Column(String(10), nullable=False)
    file = Column(String(255), nullable=False)  # File path or URL for syllabus file



<<<<<<< HEAD
# Subject Model
=======
>>>>>>> origin/try
class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    name = Column(String(100), index=True, nullable=False)
    subject_code = Column(String(20), unique=True, index=True, nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculties.id', ondelete='CASCADE'), nullable=False)
=======
    name = Column(String(20), index=True)
    subject_code= Column(String(20),unique=True, index=True)
    faculty_id = Column(Integer, ForeignKey('faculties.id'))
>>>>>>> origin/try

    faculty = relationship("Faculty", back_populates="subjects")
    papers = relationship("Paper", back_populates="subject")



class Paper(Base):
    __tablename__ = 'papers'

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    file = Column(String(255), nullable=False)  # File path or URL for paper file
    year = Column(Integer, index=True, nullable=True)
    chapter = Column(String(100), nullable=True)
    semester = Column(String(30), index=True, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    paper_type = Column(Enum(PaperType), index=True, nullable=False)

    subject = relationship("Subject", back_populates="papers")
=======
    file =  Column(String(30))
    year = Column(Integer, index=True,nullable=True)
    subject = Column(String(30))
    chapter= Column(String(30),nullable=True)
    semester = Column(String(30),index=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    # file= Column(String(30))
    paper_type = Column(Enum("Syllabus", "Notes","Question","Answer", name="Paper-type"),index=True)
>>>>>>> origin/try

    subject = relationship("Subject", back_populates="papers")



# AskQue Model (for Questions)
class AskQue(Base):
    __tablename__ = 'ask_que'

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    question = Column(String(500), nullable=False)
    question_img = Column(String(255), nullable=True)  # Path for question image if any
    faculty = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    chapter = Column(String(100), nullable=True)
    semester = Column(String(30), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
=======
    question = Column(String(500))
    question_img = Column(String(30), nullable=True)
    faculty = Column(String(10))
    subject = Column(String(30))
    chapter = Column(String(30), nullable=True)
    semester = Column(String(30), index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
>>>>>>> origin/try
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserRegister", back_populates="questions")
    answers = relationship("AnswerPost", back_populates="question", cascade="all, delete-orphan")

# AnswerPost Model (for Answers)
class AnswerPost(Base):
    __tablename__ = 'ans_post'

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    answer = Column(String(500), nullable=False)
    ans_img = Column(String(255), nullable=True)  # Path for answer image if any
    question_id = Column(Integer, ForeignKey('ask_que.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
=======
    answer = Column(String(500))
    ans_img = Column(String(30), nullable=True)
    question_id = Column(Integer, ForeignKey('ask_que.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
>>>>>>> origin/try
    timestamp = Column(DateTime, default=datetime.utcnow)

    question = relationship("AskQue", back_populates="answers")
    user = relationship("UserRegister", back_populates="answers")