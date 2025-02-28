from models.profile import Profile

class ProfileRepository:
    def __init__(self, session):
        """Инициализация репозитория."""
        self.session = session

    def create_profile(self, user_id, work_experience_description, years_of_experience, education_info, comments):
        """Создать новый профиль."""
        new_profile = Profile(
            user_id=user_id,
            work_experience_description=work_experience_description,
            years_of_experience=years_of_experience,
            education_info=education_info,
            comments=comments
        )
        self.session.add(new_profile)
        self.session.commit()

    def get_profile_by_user_id(self, user_id):
        """Получить профиль по user_id."""
        return self.session.query(Profile).filter_by(user_id=user_id).first()

    def update_profile(self, profile, work_experience_description, years_of_experience, education_info, comments):
        """Обновить профиль."""
        profile.work_experience_description = work_experience_description
        profile.years_of_experience = years_of_experience
        profile.education_info = education_info
        profile.comments = comments
        self.session.commit()