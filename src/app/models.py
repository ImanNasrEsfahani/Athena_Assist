from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from src.app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    mobile = Column(String, unique=True, nullable=False)
    telegram_chat_id = Column(Integer, nullable=True)
    active = Column(Integer, default=1)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}', mobile='{self.mobile}', " \
               f"telegram_chat_id='{self.telegram_chat_id}', active={self.active})> "


class Market(Base):
    __tablename__ = 'markets'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"<Market(id={self.id}, name='{self.name}')>"


class Pairs(Base):
    __tablename__ = 'pairs'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)
    name = Column(String, nullable=False)

    market = relationship("Market", back_populates="pairs")

    def __repr__(self):
        return f"<Pairs(id={self.id}, market_id={self.market_id}, name='{self.name}')>"


Market.pairs = relationship("Pairs", order_by=Pairs.id, back_populates="market")


class Timeframe(Base):
    __tablename__ = 'timeframes'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)
    minutes = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Timeframe(id={self.id}, name='{self.name}', minutes={self.minutes})>"


class Notifications(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String, nullable=False)
    method = Column(String)  # This can be "telegram", "sms", "email", etc.

    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notifications(id={self.id}, user_id={self.user_id}, message='{self.message}', method='{self.method}')>"


User.notifications = relationship("Notifications", order_by=Notifications.id, back_populates="user")


class Models(Base):
    __tablename__ = 'models'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    pair_id = Column(Integer, ForeignKey('pairs.id'), nullable=False)
    timeframe_id = Column(Integer, ForeignKey('timeframes.id'), nullable=False)

    pair = relationship("Pairs", back_populates="models")
    timeframe = relationship("Timeframe", back_populates="models")

    def __repr__(self):
        return f"<Models(id={self.id}, pair_id={self.pair_id}, timeframe_id={self.timeframe_id})>"


Pairs.models = relationship("Models", order_by=Models.id, back_populates="pair")
Timeframe.models = relationship("Models", order_by=Models.id, back_populates="timeframe")
