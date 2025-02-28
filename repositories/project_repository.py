from models.project import Project

class ProjectRepository:
    def __init__(self, session):
        self.session = session

    def create_project(self, title, description, budget, deadline, customer_id):
        new_project = Project(title=title, description=description, budget=budget, deadline=deadline, customer_id=customer_id)
        self.session.add(new_project)
        self.session.commit()

    def get_all_available_projects(self):
        return self.session.query(Project).filter(Project.status == 'available').all()  
    
    def get_all_projects_for_user(self):
        """Получить все проекты для обычного пользователя."""
        return self.session.query(Project).all()

    def get_projects_for_customer(self, customer_id):
        """Получить проекты только для заказчика по его ID."""
        return self.session.query(Project).filter_by(customer_id=customer_id).all()

    def get_projects_by_user_id(self, user_id):
        """Получить проекты, где пользователь является либо клиентом, либо исполнителем."""
        return self.session.query(Project).filter(
            (Project.customer_id == user_id) | (Project.executor_id == user_id)
        ).all()

    def get_all_projects(self):
         """Получить все проекты, созданные всеми заказчиками."""
         return self.session.query(Project).all()

    def get_project_by_id(self, project_id):
        """Получить проект по его ID."""
        return self.session.query(Project).filter_by(id=project_id).first()

    def delete_project(self, project_id):
        """Удалить проект по его ID."""
        project = self.get_project_by_id(project_id)
        if project:
            self.session.delete(project)
            self.session.commit()

    def update_project(self, project_id, title=None, description=None, budget=None, deadline=None):
        """Обновить проект по его ID."""
        project = self.get_project_by_id(project_id)
        if project:
            if title:
                project.title = title
            if description:
                project.description = description
            if budget:
                project.budget = budget
            if deadline:
                project.deadline = deadline
            self.session.commit()