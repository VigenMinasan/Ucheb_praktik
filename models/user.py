from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)  # Убедитесь, что unique=True, если хотите уникальные имена
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)  # 'customer' или 'executor'

    def __repr__(self):
        return f"<User  (username='{self.username}', email='{self.email}', role='{self.role}')>"
