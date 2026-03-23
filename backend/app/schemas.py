from pydantic import BaseModel, ConfigDict

class TeacherBase(BaseModel):
    first_name: str
    last_name: str

class TeacherCreate(TeacherBase):
    pass

class TeacherResponse(TeacherBase):
    id: int

    model_config = ConfigDict(from_attributes=True)