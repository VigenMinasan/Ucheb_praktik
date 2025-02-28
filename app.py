from os import abort
from flask import Flask, request, redirect, url_for, render_template, flash, session
from sqlalchemy.orm import sessionmaker
from database import init_db, SessionLocal
from repositories.user_repository import UserRepository, ProjectRepository, ProfileRepository, ApplicationRepository
from models import User, Profile
import bcrypt
from datetime import datetime
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Инициализация Flask-SocketIO
socketio = SocketIO(app)

@socketio.on('new_application')
def handle_new_application(application_data):
    emit('application_created', application_data, broadcast=True)

# Инициализация базы данных
init_db()
db_session = SessionLocal()

# Функция для аутентификации пользователя
def authenticate_user(username, password):
    user_repo = UserRepository(db_session)
    user = user_repo.get_user_by_username(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return user
    return None

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    user = authenticate_user(username, password)

    if user:
        session['user_id'] = user.id
        return redirect(url_for('executor_dashboard', user_id=user.id) if user.role == 'executor' else url_for('customer_dashboard', user_id=user.id))
    else:
        flash("Неверные учетные данные")
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        email = request.form['email']
        role = request.form['role']

        user_repo = UserRepository(db_session)
        existing_user_email = user_repo.get_user_by_email(email)

        if existing_user_email:
            error_message = 'Пользователь с таким адресом электронной почты уже существует.'
        else:
            password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
            user_repo.create_user(username, password_hash, email, role)
            flash('Регистрация успешна. Пожалуйста, войдите в систему.')
            return redirect(url_for('login'))

    return render_template('register.html', error_message=error_message)

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user_repo = UserRepository(db_session)
    user = user_repo.get_user_by_id(user_id)
    project_repo = ProjectRepository(db_session)
    projects = project_repo.get_projects_for_customer(user_id) if user.role == 'customer' else project_repo.get_all_projects_for_user()
    
    return render_template('customer_dashboard.html', user=user, projects=projects)

@app.route('/executor_dashboard/<int:user_id>', methods=['GET'])
def executor_dashboard(user_id):
    user_repo = UserRepository(db_session)
    user = user_repo.get_user_by_id(user_id)
    project_repo = ProjectRepository(db_session)
    projects = project_repo.get_all_projects()
    return render_template('executor_dashboard.html', user=user, projects=projects)

@app.route('/customer_dashboard/<int:user_id>', methods=['GET'])
def customer_dashboard(user_id):
    user_repo = UserRepository(db_session)
    user = user_repo.get_user_by_id(user_id)
    project_repo = ProjectRepository(db_session)
    projects = project_repo.get_projects_for_customer(user_id)
    return render_template('customer_dashboard.html', user=user, projects=projects)

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    user_id_session = session.get('user_id')
    if not user_id_session or user_id != user_id_session:
        return redirect(url_for('login'))

    user_repo = UserRepository(db_session)
    user = user_repo.get_user_by_id(user_id)
    if not user:
        abort(404)

    profile_repo = ProfileRepository(db_session)
    
    if request.method == 'POST':
        work_experience_description = request.form['work_experience_description']
        years_of_experience = request.form['years_of_experience']
        education_info = request.form['education_info']
        comments = request.form['comments']

        profile = profile_repo.get_profile_by_user_id(user_id)
        if profile:
            profile_repo.update_profile(profile, work_experience_description, years_of_experience, education_info, comments)
            flash('Профиль успешно обновлён.')
        else:
            new_profile = Profile(
                user_id=user_id,
                work_experience_description=work_experience_description,
                years_of_experience=years_of_experience,
                education_info=education_info,
                comments=comments
            )
            db_session.add(new_profile)
            db_session.commit()
            flash('Профиль успешно создан.')

    return render_template('profile.html', profile=profile)

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        budget = request.form['budget']
        deadline_str = request.form['deadline']
        deadline = datetime.fromisoformat(deadline_str)

        project_repo = ProjectRepository(db_session)
        project_repo.create_project(title, description, budget, deadline, user_id)

        # Отправляем событие о новой заявке
        application_data = {
            'title': title,
            'description': description,
            'budget': budget,
            'created_at': datetime.now().strftime('%Y-%m-%d'),  # Форматируем дату
            'user_id': user_id
}
        socketio.emit('application_created', application_data)


        flash('Проект успешно добавлен.')
        return redirect(url_for('dashboard'))

    return render_template('add_project.html')



@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    user_id_session = session.get('user_id')
    
    if not user_id_session:
        return redirect(url_for('login'))
    
    project_repo = ProjectRepository(db_session)
    project = project_repo.get_project_by_id(project_id)
    
    if project and project.customer_id == user_id_session:
        db_session.delete(project)
        db_session.commit()
        # Отправляем событие project_deleted
        socketio.emit('project_deleted', {'project_id': project_id})
        flash('Проект успешно удалён.')
    else:
        flash('У вас нет прав для удаления этого проекта или проект не найден.')

    return redirect(url_for('dashboard'))


project_repo = ProjectRepository(db_session)

@app.route('/withdraw/<int:project_id>', methods=['POST'])
def withdraw_project(project_id):
    project = project_repo.get_project_by_id(project_id)

    if project:
        project.count_chotcik += 1
        db_session.commit()
        print(f"Счетчик отозванных заявок для проекта {project_id} увеличен на 1. Текущий счетчик: {project.count_chotcik}")
    else:
        print(f"Проект с ID {project_id} не найден.")

    user_id = session.get('user_id')

    if user_id:

        return redirect(url_for('executor_dashboard', user_id=user_id))
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем user_id из сессии
    flash('Вы вышли из системы.')  # Сообщение о выходе
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)