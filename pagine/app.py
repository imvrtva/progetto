from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Creazione dell'app Flask
app = Flask(__name__)

# Configurazione del database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    #'postgresql+psycopg2://myuser:mypassword@localhost/mydatabase
app.config['SECRET_KEY'] = 'your_secret_key'

# Inizializzazione di SQLAlchemy
db = SQLAlchemy(app)

# Inizializzazione di Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login.login'  # Imposta la vista di login

# Definizione del modello User per SQLAlchemy e Flask-Login
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Importare i blueprint delle diverse sezioni
from pagine.homeu.homeu import home_utente_bp
from pagine.homep.homep import home_inserzionista_bp
from pagine.login.login import login_bp
from pagine.profili.profili import profili_bp
from pagine.pubblicare.pubblicare import pubblicare_bp

# Registrare i blueprint
app.register_blueprint(home_utente_bp, url_prefix='/home_utente')
app.register_blueprint(home_inserzionista_bp, url_prefix='/home_inserzionista')
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(profili_bp, url_prefix='/profili')
app.register_blueprint(pubblicare_bp, url_prefix='/pubblicare')

# Definizione della rotta per la home page
@app.route('/')
def home():
    return redirect(url_for('login.login'))

# Esecuzione dell'app
if __name__ == '__main__':
    app.run(debug=True)
