from sqlalchemy.orm import Session
from app.models.college import College
from app.schemas.college import CollegeCreate, CollegeUpdate
from app.crud.base import CRUDBase

class CRUDCollege(CRUDBase[College, CollegeCreate, CollegeUpdate]):
    pass

college = CRUDCollege(College)
