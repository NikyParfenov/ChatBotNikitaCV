import enum
import datetime

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.sql import func
from sqlalchemy import (
    Integer,
    String,
    DateTime,
)


class Base(DeclarativeBase):
    pass


class MessageRoles(str, enum.Enum):
    USER = 'user'
    ASSISTANT = 'assistant'


class ChatMessages(Base):
    __tablename__ = 'chat_messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    message_id: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    created_at: Mapped[datetime.date] = mapped_column(DateTime(timezone=True), server_default=func.now())
    role: Mapped[MessageRoles] = mapped_column(String(10), unique=False, nullable=False)
    content: Mapped[str] = mapped_column(String, unique=False, nullable=False)

    def to_openai(self) -> dict:
        return {
            'role': self.role,
            'content': self.content,
        }
    
    def retrieve_msg(self) -> dict:
        return f'[{self.created_at.strftime("%d-%m-%Y %H:%M:%S")}, {self.role.upper()}]\n{self.content}\n'
