#app/models/token_blacklist.py
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.database import Base

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    jti = Column(String, primary_key=True, index=True)  
    created_at = Column(DateTime, default=datetime.utcnow)