import datetime as _dt

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import passlib.hash as _hash

from database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    leads = relationship("Lead", back_populates="owner")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True)
    company = Column(String, index=True, default="")
    note = Column(String, default="")
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    date_last_updated = Column(DateTime, default=_dt.datetime.utcnow)

    owner = relationship("User", back_populates="leads")
