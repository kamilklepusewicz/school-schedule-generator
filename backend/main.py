from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import *
from schemas import *

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
        last_name=teacher.last_name,
        subject_id=teacher.subject_id
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@app.get("/teachers", response_model=list[TeacherResponse])
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teacher).all()
    return teachers

@app.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    new_subject = Subject(
        name=subject.name,
        classroom_type_id=subject.classroom_type_id
    )
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

@app.get("/subjects", response_model=list[SubjectResponse])
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).all()
    return subjects

@app.post("/class_groups", response_model=StudentGroupResponse, status_code=status.HTTP_201_CREATED)
def create_student_group(group: StudentGroupCreate, db: Session = Depends(get_db)):
    new_group = StudentGroup(
        name=group.name
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

@app.get("/class_groups", response_model=list[StudentGroupResponse])
def get_student_groups(db: Session = Depends(get_db)):
    groups = db.query(StudentGroup).all()
    return groups

@app.post("/class_rooms", response_model=ClassroomResponse, status_code=status.HTTP_201_CREATED)
def create_classroom(classroom: ClassroomCreate, db: Session = Depends(get_db)):
    new_classroom = Classroom(
        name=classroom.name,
        classroom_type_id=classroom.classroom_type_id
    )
    db.add(new_classroom)
    db.commit()
    db.refresh(new_classroom)
    return new_classroom

@app.get("/class_rooms", response_model=list[ClassroomResponse])
def get_classrooms(db: Session = Depends(get_db)):
    classrooms = db.query(Classroom).all()
    return classrooms

@app.post("/classes", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(lesson: LessonCreate, db: Session = Depends(get_db)):
    new_lesson = Lesson(
        subject_id=lesson.subject_id,
        classroom_id=lesson.classroom_id,
        teacher_id=lesson.teacher_id,
        group_id=lesson.group_id,
        slot=lesson.slot,
        day=lesson.day
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson

@app.get("/classes", response_model=list[LessonResponse])
def get_lessons(db: Session = Depends(get_db)):
    lessons = db.query(Lesson).all()
    return lessons

@app.post("/classroom_types", response_model=ClassroomTypeResponse, status_code=status.HTTP_201_CREATED)
def create_classroom_type(classroom_type: ClassroomTypeCreate, db: Session = Depends(get_db)):
    new_classroom_type = ClassroomType(
        name=classroom_type.name
    )
    db.add(new_classroom_type)
    db.commit()
    db.refresh(new_classroom_type)
    return new_classroom_type

@app.get("/classroom_types", response_model=list[ClassroomTypeResponse])
def get_classroom_types(db: Session = Depends(get_db)):
    classroom_types = db.query(ClassroomType).all()
    return classroom_types

@app.post("/lesson_counts", response_model=list[LessonCountResponse], status_code=status.HTTP_201_CREATED)
def create_lesson_count(lesson_count: LessonCountCreate, db: Session = Depends(get_db)):
    new_lesson_count = LessonCount(
        student_group_id = lesson_count.student_group_id,
        subject_id = lesson_count.subject_id,
        hours = lesson_count.hours
    )
    db.add(new_lesson_count)
    db.commit()
    db.refresh(new_lesson_count)
    return new_lesson_count

@app.get("/lesson_counts", response_model=list[LessonCountResponse])
def get_lesson_count(db: Session = Depends(get_db)):
    lesson_counts = db.query(LessonCount).all()
    return lesson_counts