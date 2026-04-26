from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database import Base


class Teacher(Base):
    __tablename__ = "teacher"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey("subject.id"), nullable=False)

class StudentGroup(Base):
    __tablename__ = "student_group"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class Subject(Base):
    __tablename__ = "subject"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class Classroom(Base):
    __tablename__ = "classroom"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class Lesson(Base):
    __tablename__ = "lesson"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subject.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classroom.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("group.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    description = Column(String, nullable=True)
    ##status = Column(String, nullable=False)