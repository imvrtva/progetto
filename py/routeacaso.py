#route delle pagine
from flask import Blueprint, render_template
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from database import all

#--------------------- inzerzionista ----------------------#

home_inserzionista_bp = Blueprint('home_inserzionista', __name__)

@home_inserzionista_bp.route('/')
@login_required
def home():
    return render_template('home_inserzionista.html')

pubblicare_bp = Blueprint('pubblicare', __name__)

@pubblicare_bp.route('/', methods=['GET', 'POST'])
@login_required
def publish():
    if request.method == 'POST':
        content = request.form.get('content')
        # Logica per salvare il post o l'inserzione
        return redirect(url_for('home_utente.home'))
    return render_template('pubblicare.html')

#------------------------ utente -------------------------#

home_utente_bp = Blueprint('home_utente', __name__)

@home_utente_bp.route('/')
@login_required
def home():
    return render_template('home_utente.html')

pubblicare_bp = Blueprint('pubblicare', __name__)

@pubblicare_bp.route('/', methods=['GET', 'POST'])
@login_required
def publish():
    if request.method == 'POST':
        content = request.form.get('content')
        # Logica per salvare il post o l'inserzione
        return redirect(url_for('home_utente.home'))
    return render_template('pubblicare.html')

#------------------------ login -------------------------#

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

#------------------------ logout -------------------------#

@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.login'))

#--------------------- registrazione ----------------------#

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

#------------------------ profilo utente -------------------------#

profili_bp = Blueprint('profili', __name__)

@profili_bp.route('/<user_id>')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    return render_template('profili.html', user=user)
