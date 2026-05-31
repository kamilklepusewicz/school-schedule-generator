from database import SessionLocal
from models import Teacher, Classroom, StudentGroup, LessonCount, Subject

def fetch_data_for_algorithm():
    db = SessionLocal()
    try:
        teachers = db.query(Teacher).all()
        classrooms = db.query(Classroom).all()
        groups = db.query(StudentGroup).all()
        lesson_counts = db.query(LessonCount).all()
        subjects = db.query(Subject).all()

        data = {
            "teachers": [{"id": t.id, "subject_id": t.subject_id} for t in teachers],
            "classrooms": [{"id": c.id, "type_id": c.classroom_type_id} for c in classrooms],
            "groups": [{"id": g.id, "name": g.name} for g in groups],
            "subjects": [{"id": s.id, "type_id": s.classroom_type_id} for s in subjects],
            "demands": [
                {
                    "group_id": lc.student_group_id, 
                    "subject_id": lc.subject_id, 
                    "hours": lc.hours
                } 
                for lc in lesson_counts
            ]
        }
        return data
    finally:
        db.close()