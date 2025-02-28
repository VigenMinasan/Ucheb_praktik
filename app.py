from flask import Flask, request, redirect, url_for, render_template, flash, session
from database import init_db, SessionLocal

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Инициализация базы данных
init_db()
db_session = SessionLocal()

@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)