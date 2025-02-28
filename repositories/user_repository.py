from models.user import User

class UserRepository:
    def __init__(self, session):
        """Инициализация репозитория."""
        self.session = session

    def create_user(self, username, password_hash, email, role):
        """Создать нового пользователя."""
        new_user = User(username=username, password_hash=password_hash, email=email, role=role)
        self.session.add(new_user)
        self.session.commit()
    def get_user_by_username(self, username):
        """Получить пользователя по username."""
        return self.session.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id):
        """Получить пользователя по id."""
        return self.session.query(User).filter_by(id=user_id).first()
    
    def get_user_by_email(self, email):
        """Получить пользователя по email."""
        return self.session.query(User).filter_by(email=email).first()