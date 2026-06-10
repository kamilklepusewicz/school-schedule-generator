from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import *
from schemas import *
from solverAlgorithm import algorytm_planu_lekcji

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


# ENDPOINTY NAUCZYCIELI
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


@app.put("/teachers/{teacher_id}", response_model=TeacherResponse)
def update_teacher(teacher_id: int, teacher: TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nauczyciel nie znaleziony")
    
    db_teacher.first_name = teacher.first_name
    db_teacher.last_name = teacher.last_name
    db_teacher.subject_id = teacher.subject_id
    
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@app.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nauczyciel nie znaleziony")
    
    db.delete(db_teacher)
    db.commit()
    return


# ENDPOINTY PRZEDMIOTÓW
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


@app.put("/subjects/{subject_id}", response_model=SubjectResponse)
def update_subject(subject_id: int, subject: SubjectCreate, db: Session = Depends(get_db)):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Przedmiot nie znaleziony")
    
    db_subject.name = subject.name
    db_subject.classroom_type_id = subject.classroom_type_id
    
    db.commit()
    db.refresh(db_subject)
    return db_subject


@app.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Przedmiot nie znaleziony")
    
    db.delete(db_subject)
    db.commit()
    return


# ENDPOINTY KLAS UCZNIOWSKICH
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


@app.put("/class_groups/{group_id}", response_model=StudentGroupResponse)
def update_student_group(group_id: int, group: StudentGroupCreate, db: Session = Depends(get_db)):
    db_group = db.query(StudentGroup).filter(StudentGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupa nie znaleziona")
    
    db_group.name = group.name
    
    db.commit()
    db.refresh(db_group)
    return db_group


@app.delete("/class_groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(StudentGroup).filter(StudentGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupa nie znaleziona")
    
    db.delete(db_group)
    db.commit()
    return


# ENDPOINTY SAL LEKCYJNYCH
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


@app.put("/class_rooms/{classroom_id}", response_model=ClassroomResponse)
def update_classroom(classroom_id: int, classroom: ClassroomCreate, db: Session = Depends(get_db)):
    db_classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not db_classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala nie znaleziona")
    
    db_classroom.name = classroom.name
    db_classroom.classroom_type_id = classroom.classroom_type_id
    
    db.commit()
    db.refresh(db_classroom)
    return db_classroom


@app.delete("/class_rooms/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_classroom(classroom_id: int, db: Session = Depends(get_db)):
    db_classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not db_classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala nie znaleziona")
    
    db.delete(db_classroom)
    db.commit()
    return


# ENDPOINTY LEKCJI
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


@app.put("/classes/{lesson_id}", response_model=LessonResponse)
def update_lesson(lesson_id: int, lesson: LessonCreate, db: Session = Depends(get_db)):
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lekcja nie znaleziona")
    
    db_lesson.subject_id = lesson.subject_id
    db_lesson.classroom_id = lesson.classroom_id
    db_lesson.teacher_id = lesson.teacher_id
    db_lesson.group_id = lesson.group_id
    db_lesson.slot = lesson.slot
    db_lesson.day = lesson.day
    
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@app.delete("/classes/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lekcja nie znaleziona")
    
    db.delete(db_lesson)
    db.commit()
    return


# ENDPOINTY TYPÓW SAL
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


@app.put("/classroom_types/{type_id}", response_model=ClassroomTypeResponse)
def update_classroom_type(type_id: int, classroom_type: ClassroomTypeCreate, db: Session = Depends(get_db)):
    db_type = db.query(ClassroomType).filter(ClassroomType.id == type_id).first()
    if not db_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Typ sali nie znaleziony")
    
    db_type.name = classroom_type.name
    
    db.commit()
    db.refresh(db_type)
    return db_type


@app.delete("/classroom_types/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_classroom_type(type_id: int, db: Session = Depends(get_db)):
    db_type = db.query(ClassroomType).filter(ClassroomType.id == type_id).first()
    if not db_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Typ sali nie znaleziony")
    
    db.delete(db_type)
    db.commit()
    return


# ENDPOINTY LICZBY GODZIN PRZEDMIOTU DLA GRUPY
@app.post("/lesson_counts", response_model=list[LessonCountResponse], status_code=status.HTTP_201_CREATED)
def create_lesson_count(lesson_counts: list[LessonCountCreate], db: Session = Depends(get_db)):
    new_lesson_counts = []
    for lesson_count in lesson_counts:
        new_lesson_count = LessonCount(
            student_group_id = lesson_count.student_group_id,
            subject_id = lesson_count.subject_id,
            hours = lesson_count.hours
        )
        new_lesson_counts.append(new_lesson_count)

    db.add_all(new_lesson_counts)
    db.commit()
    
    for lesson_count in new_lesson_counts:
        db.refresh(lesson_count)

    return new_lesson_counts


@app.get("/lesson_counts", response_model=list[LessonCountResponse])
def get_lesson_count(db: Session = Depends(get_db)):
    lesson_counts = db.query(LessonCount).all()
    return lesson_counts


@app.put("/lesson_counts/{count_id}", response_model=LessonCountResponse)
def update_lesson_count(count_id: int, lesson_count: LessonCountCreate, db: Session = Depends(get_db)):
    db_count = db.query(LessonCount).filter(LessonCount.id == count_id).first()
    if not db_count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Przydział nie znaleziony")
    
    db_count.student_group_id = lesson_count.student_group_id
    db_count.subject_id = lesson_count.subject_id
    db_count.hours = lesson_count.hours
    
    db.commit()
    db.refresh(db_count)
    return db_count


@app.delete("/lesson_counts/{count_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson_count(count_id: int, db: Session = Depends(get_db)):
    db_count = db.query(LessonCount).filter(LessonCount.id == count_id).first()
    if not db_count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Przydział nie znaleziony")
    
    db.delete(db_count)
    db.commit()
    return


@app.post("/schedule/generate", status_code=status.HTTP_200_OK)
def generate_school_schedule(db: Session = Depends(get_db)):
    raw_schedule = algorytm_planu_lekcji()
    
    if not raw_schedule:
        raise HTTPException(status_code=400, detail="Algorytm nie ułożył planu przy tych ograniczeniach")
    
    db.query(Lesson).delete()
    
    for item in raw_schedule:
        new_lesson = Lesson(
            subject_id=item["subject_id"],
            classroom_id=item["classroom_id"],
            teacher_id=item["teacher_id"],
            group_id=item["group_id"],
            slot=item["slot"],
            day=item["day"]
        )
        db.add(new_lesson)
        
    db.commit()
    
    return {"message": "Plan wygenerowany i zapisany pomyślnie"}