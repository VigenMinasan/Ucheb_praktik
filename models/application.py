from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from database import Base
from datetime import datetime

class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default='pending')  # 'pending', 'accepted', 'rejected'

    def __repr__(self):
        return f"<Application(project_id='{self.project_id}', user_id='{self.user_id}', status='{self.status}')>"