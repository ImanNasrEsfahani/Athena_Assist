from sqlalchemy.orm import Session
from .models import User


def create_user(db: Session, name: str, email: str, mobile: str, telegram_chat_id: int) -> User:
    # Create a new User instance
    new_user = User(name=name, email=email, mobile=mobile, telegram_chat_id=telegram_chat_id, active=True)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
