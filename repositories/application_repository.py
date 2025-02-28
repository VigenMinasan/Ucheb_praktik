from models.application import Application

class ApplicationRepository:
    def __init__(self, session):
        self.session = session

    def create_application(self, project_id, user_id, message):
        new_application = Application(project_id=project_id, user_id=user_id, message=message)
        self.session.add(new_application)
        self.session.commit()


