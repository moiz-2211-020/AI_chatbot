from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True)  # Storing user ID or email as plain string
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
