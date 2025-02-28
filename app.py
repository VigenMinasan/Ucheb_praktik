from os import abort
from flask import Flask, request, redirect, url_for, render_template, flash, session
from sqlalchemy.orm import sessionmaker
from database import init_db, SessionLocal
from repositories.user_repository import UserRepository
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

if __name__ == '__main__':
    app.run(debug=True)