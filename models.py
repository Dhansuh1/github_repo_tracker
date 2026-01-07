from sqlalchemy import Column, Integer, String
from database import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    stars = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
