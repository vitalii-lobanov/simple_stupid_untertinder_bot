# app/services/user_service.py
from app.models.user import User
from app.database.engine import get_db_session
from app.utils.debug import logger

def add_user_to_database(user_id, user_status):
    session = get_db_session()
    new_user = User(id=user_id, status=user_status)
    try:
        session.add(new_user)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# app/services/user_service.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.database.engine import get_db_session

def get_user_status(user_id: int) -> str:
    session: Session = get_db_session()
    try:
        user_status = session.query(User.status).filter(User.id == user_id).scalar()
        return user_status
    finally:
        session.close()

def update_user_status(user_id: int, new_status: str) -> None:
    session: Session = get_db_session()
    try:
        user = session.query(User).filter(User.id == user_id).one()
        user.status = new_status
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()