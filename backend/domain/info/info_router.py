from fastapi import APIRouter, Depends
from starlette import status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from models import User
from database import get_db

router = APIRouter(
    prefix="/api/info",
)


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


def get_info(db: Session, user_id: int):
    info = db.query(Info).get(user_id)
    return info


def create_info(db: Session, info_create: InfoCreate):
    db_info = User(name=info_create.name)
    db.add(db_info)
    db.commit()


@router.get("/detail/{user_id}", response_model=Info)
def info_detail(user_id: int, db: Session = Depends(get_db)):
    info = get_info(db, user_id=user_id)
    return info


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def info_create(_info_create: InfoCreate,
                db: Session = Depends(get_db)):
    create_info(db=db, info_create=_info_create)
