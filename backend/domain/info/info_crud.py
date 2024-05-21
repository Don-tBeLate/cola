from sqlalchemy.orm import Session

from domain.info.info_schema import Info, InfoCreate
from models import User


def get_info(db: Session, user_id: int):
    info = db.query(Info).get(user_id)
    return info


def create_info(db: Session, info_create: InfoCreate):
    db_info = User(name=info_create.name)
    db.add(db_info)
    db.commit()
