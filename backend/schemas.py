from pydantic import BaseModel, ConfigDict
from datetime import datetime
## Teacher Schemas
class TeacherBase(BaseModel):
    first_name: str
    last_name: str
    subject_id: int

class TeacherCreate(TeacherBase):
    pass

class TeacherResponse(TeacherBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
##=================================================
# Student Group Schemas
class StudentGroupBase(BaseModel):
    name: str

class StudentGroupCreate(StudentGroupBase):
    pass

class StudentGroupResponse(StudentGroupBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

##=================================================
# Subject Schemas
class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

##=================================================
# Classroom Schemas
class ClassroomBase(BaseModel):
    name: str

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomResponse(ClassroomBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

##=================================================
# Lesson Schemas
class LessonBase(BaseModel):
    subject_id: int
    classroom_id: int
    teacher_id: int
    group_id: int
    start_time: datetime
    end_time: datetime
    description: str | None = None
    ##status: str

class LessonCreate(LessonBase):
    pass

class LessonResponse(LessonBase):
    id: int

    model_config = ConfigDict(from_attributes=True)