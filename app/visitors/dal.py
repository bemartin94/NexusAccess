from sqlalchemy.orm import Session
from app.visitors import schemas
from core.models import Visitor

class VisitorDAL:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all(self, skip: int = 0, limit: int = 100) -> list[schemas.VisitorResponse]:
        visitors = self.db.query(Visitor).offset(skip).limit(limit).all()
        return [schemas.VisitorResponse.model_validate(v) for v in visitors]

    def get_by_id(self, visitor_id: int) -> schemas.VisitorResponse | None:
        visitor = self.db.query(Visitor).filter(Visitor.id == visitor_id).first()
        if visitor:
            return schemas.VisitorResponse.model_validate(visitor)
        return None

    def create(self, visitor_create: schemas.VisitorCreate) -> schemas.VisitorResponse:
        visitor_data = visitor_create.model_dump()
        visitor = Visitor(**visitor_data)
        self.db.add(visitor)
        self.db.commit()
        self.db.refresh(visitor)
        return schemas.VisitorResponse.model_validate(visitor)

    def update(self, visitor_id: int, visitor_update: schemas.VisitorUpdate) -> schemas.VisitorResponse | None:
        visitor = self.db.query(Visitor).filter(Visitor.id == visitor_id).first()
        if not visitor:
            return None

        update_data = visitor_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(visitor, key, value)

        self.db.commit()
        self.db.refresh(visitor)
        return schemas.VisitorResponse.model_validate(visitor)

    def delete(self, visitor_id: int) -> bool:
        visitor = self.db.query(Visitor).filter(Visitor.id == visitor_id).first()
        if not visitor:
            return False
        self.db.delete(visitor)
        self.db.commit()
        return True
