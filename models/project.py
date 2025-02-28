from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    budget = Column(Integer, nullable=False)
    deadline = Column(DateTime, nullable=False)  # Можно использовать DateTime
    customer_id = Column(Integer, ForeignKey('users.id'))
    executor_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default='active')  # 'active', 'completed', etc.
    count_chotcik = Column(Integer, default=0)

    customer = relationship("User", foreign_keys=[customer_id])
    executor = relationship("User", foreign_keys=[executor_id])

    def __repr__(self):
        return f"<Project(title='{self.title}', budget='{self.budget}')>"