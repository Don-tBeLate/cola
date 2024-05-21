from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.info import info_schema, info_crud

router = APIRouter(
    prefix="/api/info",
)


@router.get("/detail/{user_id}", response_model=info_schema.Info)
def info_detail(user_id: int, db: Session = Depends(get_db)):
    info = info_crud.get_info(db, user_id=user_id)
    return info


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def info_create(_info_create: info_schema.InfoCreate,
                db: Session = Depends(get_db)):
    info_crud.create_info(db=db, info_create=_info_create)
