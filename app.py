# Questo file è il cuore dell'applicazione web, integrando database, 
# autenticazione e routing in una struttura organizzata e modulare.

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


# Questa sezione importa le librerie necessarie:
# Flask: il framework principale per creare l'applicazione web.
# render_template, redirect, url_for: funzioni ausiliarie di Flask 
# per il rendering delle pagine HTML e la gestione delle redirezioni.
# SQLAlchemy: un ORM (Object Relational Mapper) per interagire con il database.
# LoginManager: un'estensione di Flask-Login per gestire l'autenticazione.

#----------------------------------------------------------------#

# Creazione dell'app Flask
# Qui viene creata l'istanza principale dell'applicazione Flask.

app = Flask(__name__)
bcrypt = Bcrypt(app)

#----------------------------------------------------------------#

# Questa parte configura l'applicazione per utilizzare un 
# database SQLite chiamato database.db (la riga commentata 
# mostra come potrebbe essere configurato un database PostgreSQL). 
# SECRET_KEY è una chiave segreta usata da Flask per la gestione delle sessioni 
# e altre funzionalità di sicurezza.

# Configurazione del database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    #'postgresql+psycopg2://myuser:mypassword@localhost/mydatabase
app.config['SECRET_KEY'] = 'your_secret_key'

#----------------------------------------------------------------#

# Inizializza l'oggetto SQLAlchemy con l'app Flask, 
# permettendo l'interazione con il database.

# Inizializzazione di SQLAlchemy
db = SQLAlchemy(app)

#----------------------------------------------------------------#


# Inizializza l'oggetto LoginManager per gestire l'autenticazione degli utenti. 
# login_view imposta la rotta a cui Flask-Login reindirizzerà gli utenti non 
# autenticati.

# Inizializzazione di Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login.login'  # Imposta la vista di login

#----------------------------------------------------------------#

# Definisce il modello User, che rappresenta la tabella degli utenti nel database. 
# Include metodi richiesti da Flask-Login per gestire lo stato di autenticazione 
# degli utenti (is_active, get_id, is_authenticated, is_anonymous).

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
    
#----------------------------------------------------------------#
 
# Definisce una funzione di callback che Flask-Login utilizza per caricare 
# un utente dal database, dato il suo ID.

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#----------------------------------------------------------------#

# Importa i blueprint delle diverse sezioni dell'applicazione. 
# I blueprint sono componenti modulari che organizzano il codice 
# per differenti parti dell'applicazione (ad esempio, pagine utente, 
# pagine login, ecc.).

# Importare i blueprint delle diverse sezioni
from py.homeu.homeu import home_utente_bp
from py.homep.homep import home_inserzionista_bp
from py.login.login import login_bp
from py.profili.profili import profili_bp
from py.pubblicare.pubblicare import pubblicare_bp

#----------------------------------------------------------------#

# Registra i blueprint nell'app principale, specificando il prefisso URL 
# per ciascuno. Questo aiuta a organizzare le rotte in modo modulare.

# Registrare i blueprint
app.register_blueprint(home_utente_bp, url_prefix='/home_utente')
app.register_blueprint(home_inserzionista_bp, url_prefix='/home_inserzionista')
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(profili_bp, url_prefix='/profili')
app.register_blueprint(pubblicare_bp, url_prefix='/pubblicare')

#----------------------------------------------------------------#

# Definisce la rotta principale (/) dell'applicazione. 
# Quando un utente visita la home page, viene reindirizzato alla pagina di login.

# Definizione della rotta per la home page
@app.route('/')
def home():
    return redirect(url_for('login.login'))

#----------------------------------------------------------------#

# Infine, avvia l'applicazione Flask in modalità debug, 
# che fornisce utili messaggi di errore e consente il 
# riavvio automatico del server durante lo sviluppo.

# Esecuzione dell'app
if __name__ == '__main__':
    app.run(debug=True)
