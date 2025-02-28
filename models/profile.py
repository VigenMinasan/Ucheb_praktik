from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    work_experience_description = Column(String)
    years_of_experience = Column(Integer)
    education_info = Column(String)
    comments = Column(String)

    def __repr__(self):
        return f"<Profile(user_id='{self.user_id}', experience='{self.years_of_experience}')>"