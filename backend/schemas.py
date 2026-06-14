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
    classroom_type_id: int

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

##=================================================
# Classroom Schemas
class ClassroomBase(BaseModel):
    name: str
    classroom_type_id: int

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomResponse(ClassroomBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ClassroomTypeBase(BaseModel):
    name: str

class ClassroomTypeCreate(ClassroomTypeBase):
    pass

class ClassroomTypeResponse(ClassroomTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

##=================================================
# Lesson Schemas
class LessonBase(BaseModel):
    subject_id: int
    classroom_id: int
    teacher_id: int
    group_id: int
    slot: int
    day: int

class LessonCreate(LessonBase):
    pass

class LessonResponse(LessonBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class LessonCountBase(BaseModel):
    student_group_id: int
    subject_id: int
    hours: int

class LessonCountCreate(LessonCountBase):
    pass

class LessonCountResponse(LessonCountBase):
    id: int

    model_config = ConfigDict(from_attributes=True)