from pydantic import BaseModel, field_validator


class Info(BaseModel):
    id: int
    name: str
    url: str

    class Config:
        orm_mode = True


class InfoCreate(BaseModel):
    name: str

    @field_validator('name')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("ERROR: NO NAME")
        return v
