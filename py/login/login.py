from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from your_database_model import db, User

login_bp = Blueprint('login', __name__)

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'user':
                return redirect(url_for('home_utente.home'))
            elif user.role == 'advertiser':
                return redirect(url_for('home_inserzionista.home'))
        else:
            flash('Login fallito. Controlla email e password.')
    return render_template('login.html')

@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.login'))

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        if role == 'user':
            return redirect(url_for('home_utente.home'))
        elif role == 'advertiser':
            return redirect(url_for('home_inserzionista.home'))
    return render_template('register.html')
