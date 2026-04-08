from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import Teacher
from schemas import TeacherCreate, TeacherResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # na start najprościej, potem można zawęzić do Reacta
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Backend działa"}


@app.post("/teachers", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    new_teacher = Teacher(
        first_name=teacher.first_name,
        last_name=teacher.last_name
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@app.get("/teachers", response_model=list[TeacherResponse])
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teacher).all()
    return teachers