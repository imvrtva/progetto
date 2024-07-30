from flask import Flask, request, url_for, redirect, render_template, flash, Blueprint, current_app,jsonify, session, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, BLOB, ForeignKey, TIMESTAMP, Date, func
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
import os
import re
from enum import Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Enum as SQLAlchemyEnum
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime, timezone, timedelta
import pytz
import humanize

#------------------------ accesso server -------------------------#

app = Flask(__name__, static_folder='contenuti')
app.config['SECRET_KEY'] = 'stringasegreta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ciao@localhost:5433/progettobasi'
UPLOAD_FOLDER = 'contenuti'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'contenuti')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login.log'
login_manager.init_app(app)
bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#------------------------ creazione database -------------------------#

class Ruolo(Enum):
    utente = "utente"
    pubblicitari = "pubblicitari"

class Sesso(Enum):
    maschio = "maschio"
    femmina = "femmina"
    altro = "altro"
    tutti="tutti"


class Users(UserMixin, db.Model):
    __tablename__ = 'users'

    id_utente = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    immagine = Column(String(100), nullable=True)
    nome = Column(String(50), unique=False, nullable=False)
    cognome = Column(String(50), unique=False, nullable=False)
    password_ = Column(String(150), nullable=False)  # Changed to password_hash
    email = Column(String(150), unique=True, nullable=False)
    sesso = Column(SQLAlchemyEnum(Sesso))
    eta = Column(Integer, unique=False, nullable=False)
    ruolo = Column(SQLAlchemyEnum(Ruolo))
    bio = Column(String(250), unique=False, nullable=True)


    def __init__(self, username, nome, cognome, password_, email, sesso, eta, ruolo, immagine=None, bio=None):
    #    self.id_utente = id_utente
        self.username = username
        self.immagine = immagine
        self.nome = nome
        self.cognome = cognome
        self.password_ = password_
        self.email = email
        self.sesso = sesso
        self.eta = eta
        self.ruolo = ruolo
        self.bio = bio

    # Property for password handling
    def get_id(self):
        return self.id_utente

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')


    def verify_password(self, password):
        return self.password_ == password

    def url_photo(self):
        if self.immagine:
            return '/contenuti/' + self.immagine
        else:
            return None
        
    @property
    def follower_count(self):
        return Amici.query.filter_by(user_amico=self.id_utente).count()

    @property
    def following_count(self):
        return Amici.query.filter_by(io_utente=self.id_utente).count()

    @property
    def post_count(self):
        return Post.query.filter_by(utente=self.id_utente).count()
    
    def has_liked_post(self, post):
        return PostLikes.query.filter(PostLikes.post_id == post.id, PostLikes.utente_id == self.id_utente).count() > 0

    def url_photo(self):
        if self.immagine:
            return '/contenuti/' + self.immagine
        else:
            return '/contenuti/default_profile.png'  # Un percorso di immagine di default

    @property
    def is_pubblicitario(self):
        return self.ruolo == Ruolo.pubblicitari
    
    def id(self):
        return self.id_utente

class Interessi(db.Model, UserMixin):
    __tablename__ = 'interessi'

    id_interessi = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), unique=False, nullable=False)

    def __init__(self, id_interessi , nome):
        self.id_interessi= id_interessi
        self.nome = nome

class UserInteressi(db.Model, UserMixin):
    __tablename__ = 'user_interessi'

    utente_id = Column(Integer, ForeignKey('users.id_utente'), nullable=False, primary_key=True)
    id_interessi = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False, primary_key=True)

    def __init__(self, utente_id, id_interessi):
        self.utente_id = utente_id
        self.id_interessi = id_interessi

class Amici(db.Model, UserMixin):
    __tablename__ = 'amici'

    id_amicizia= Column(Integer, primary_key=True, autoincrement=True)
    io_utente = Column(Integer, ForeignKey('users.id_utente'), nullable=False, primary_key=True)
    user_amico = Column(Integer, ForeignKey('users.id_utente'), nullable=False, primary_key=True)
    seguito_at= Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    def init(self, id_amicizia, io_utente, user_amico, seguito_at):
        self.id_amicizia = id_amicizia
        self.io_utente = io_utente
        self.user_amico = user_amico
        self.seguito_at=seguito_at


class Post(db.Model, UserMixin):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    utente = Column(Integer, ForeignKey('users.id_utente'), nullable=False)
    media = Column(String(255), nullable=True)
    tipo_post = Column(SQLAlchemyEnum('immagini', 'video', 'testo', name='tipo_post'))
    data_creazione = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    testo = Column(Text, nullable=True)

    post_likes = relationship('PostLikes', backref='post', lazy='dynamic')

    def __init__(self, utente, tipo_post, testo=None, media=None):
        self.utente = utente
        self.tipo_post = tipo_post
        self.testo = testo
        self.media = media

    def url_photo(self):
        return '/contenuti/' + self.cover_picture
    
    @property
    def likes_count(self):
        return self.post_likes.count()

class PostComments(db.Model, UserMixin):
    __tablename__ = 'post_comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    utente_id = Column(Integer, ForeignKey('users.id_utente'))  # Aggiornato il nome della colonna
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)

    post = relationship('Post', backref='comments')
    utente = relationship('Users', backref='comments')

    def __init__(self, post_id, utente_id, content=None):
        self.post_id = post_id
        self.utente_id = utente_id
        self.content = content

class PostLikes(db.Model, UserMixin):
    __tablename__ = 'post_likes'

    post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    utente_id = Column(Integer, ForeignKey('users.id_utente'), primary_key=True)  # Aggiornato il nome della colonna
    clicked_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)


    def __init__(self, post_id, utente_id):
        self.post_id = post_id
        self.utente_id = utente_id
    

class Annunci(db.Model, UserMixin):
    __tablename__ = 'annunci'

    id = Column(Integer, primary_key=True, autoincrement=True)
    advertiser_id = Column(Integer, ForeignKey('users.id_utente'), nullable=False)
    tipo_post = Column(SQLAlchemyEnum('immagini', 'video', 'testo', name='tipo_post'))
    sesso_target = Column(SQLAlchemyEnum(Sesso))
    media = Column(String(255), nullable=True)
    eta_target = Column(Integer, unique=False, nullable=False)
    interesse_target = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False)
    
    inizio = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)
    fine = Column(Date, default=func.current_timestamp())

    testo = Column(String(255), nullable=True)  # Questo Ã¨ corretto
    titolo = Column(String(255), nullable=True)  # Nuovo campo per il titolo
    didascalia = Column(Text, nullable=True)      # Nuovo campo per la didascalia

    def __init__(self, advertiser_id, tipo_post, sesso_target, eta_target, interesse_target, inizio, fine, testo,  titolo, didascalia, media):
        self.advertiser_id = advertiser_id
        self.tipo_post = tipo_post
        self.sesso_target = sesso_target
        self.eta_target = eta_target
        self.interesse_target = interesse_target

        self.inizio= inizio
        self.fine = fine
        self.testo=testo
        self.titolo=titolo
        self.didascalia=didascalia
        self.media = media

        
        
class AnnunciClicks(db.Model):
    __tablename__ = 'annunci_clicks'

    annuncio_id = Column(Integer, ForeignKey('annunci.id'), primary_key=True)
    utente_id = Column(Integer, ForeignKey('users.id_utente'), primary_key=True)
    clicked_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)

    def __init__(self, annuncio_id, utente_id, clicked_at ):
        self.annuncio_id = annuncio_id
        self.utente_id = utente_id
        self.clicked_at = clicked_at 


class AnnunciComments(db.Model):
    __tablename__ = 'annunci_comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    annuncio_id = Column(Integer, ForeignKey('annunci.id'), nullable=False)
    utente_id = Column(Integer, ForeignKey('users.id_utente'), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)

    def __init__(self, annuncio_id, utente_id, content ,created_at ):
        self.annuncio_id = annuncio_id
        self.utente_id = utente_id
        self.content = content
        self.created_at = created_at


       
class AnnunciLikes(db.Model, UserMixin):
    __tablename__ = 'annunci_likes'

    annuncio_id = Column(Integer, ForeignKey('annunci.id'), primary_key=True)
    utente_id = Column(Integer, ForeignKey('users.id_utente'), primary_key=True)  # Modificato in user_id
    clicked_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)

    def __init__(self, annuncio_id, utente_id):
        self.annuncio_id = annuncio_id
        self.utente_id = utente_id


class Messaggi(db.Model):
    __tablename__ = 'messaggi'

    id = Column(Integer, primary_key=True, autoincrement=True)
    testo = Column(Text, nullable=False)
    mittente_id = Column(Integer, ForeignKey('users.id_utente'), nullable=False)
    destinatario_id = Column(Integer, ForeignKey('users.id_utente'), nullable=False)
    creato_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)
    postinviato = Column(Integer, ForeignKey('posts.id'), nullable=True)

    # Relationships
    mittente = relationship('Users', foreign_keys=[mittente_id], backref='messaggi_inviati')
    destinatario = relationship('Users', foreign_keys=[destinatario_id], backref='messaggi_ricevuti')
    post = relationship('Post', 
                        backref='messaggi_foto', 
                        foreign_keys=[postinviato],
                        primaryjoin='Messaggi.postinviato == Post.id')

    def __init__(self, testo, mittente_id, destinatario_id, postinviato):
        self.testo = testo
        self.mittente_id = mittente_id
        self.destinatario_id = destinatario_id
        self.postinviato = postinviato

    def __repr__(self):
        return f"<Messaggio(id={self.id}, mittente_id={self.mittente_id}, destinatario_id={self.destinatario_id}, creato_at={self.creato_at})>"


# Ensure all tables are created within the application context
with app.app_context():
    db.create_all()

#------------------------ funzioni utili -------------------------#

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


##controllo password
def check_password(password):
    length_error = len(password) < 8
    digit_error = re.search(r"\d", password) is None
    uppercase_error = re.search(r"[A-Z]", password) is None
    lowercase_error = re.search(r"[a-z]", password) is None

    return not (length_error or digit_error or uppercase_error or lowercase_error)

##controllo mail
def check_email(email):
    regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Z|a-z]{2,}\b'
    return not re.fullmatch(regex_email, email)

def crea_annuncio(user_id, tipo_post, sesso_target, eta_target, nome_interesse, durata_annuncio, testo=None, titolo=None, didascalia=None, media=None):
    # Trova l'ID dell'interesse basato sul nome
    interesse = db.session.query(Interessi).filter_by(nome=nome_interesse).first()
    if not interesse:
        return "Interesse non trovato."
    
    valid_sesso_targets = ['maschio', 'femmina', 'tutti']
    if sesso_target not in valid_sesso_targets:
        return f"Sesso target non valido. Deve essere uno di: {', '.join(valid_sesso_targets)}."
    
    try:
        fine = datetime.now() + timedelta(days=durata_annuncio)
        
        annuncio = Annunci(
            advertiser_id=user_id,
            tipo_post=tipo_post,
            sesso_target=sesso_target,
            eta_target=eta_target,
            interesse_target=interesse.id_interessi,
            inizio=datetime.now(),
            fine=fine,
            testo=testo,
            titolo=titolo,
            didascalia=didascalia,
            media=media
        )

        db.session.add(annuncio)
        db.session.commit()

        return annuncio

    except IntegrityError:
        db.session.rollback()
        return "Errore di integrità del database."
    except Exception as e:
        db.session.rollback()
        return str(e)




#------------------------ rotte sito internet -------------------------#

    #------------------------ log in e log out, registrazione -------------------------#

    ## login

@app.route('/', methods=['GET', 'POST'])
def log():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email e password sono richiesti", category="alert alert-warning")
            return redirect(url_for('log'))

        user = Users.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            login_user(user)
            session['id_utente'] = user.id_utente
            session['role'] = user.ruolo.value

            if user.ruolo == Ruolo.utente:
                return redirect(url_for('utente', id_utente=user.id_utente))
            elif user.ruolo == Ruolo.pubblicitari:
                return redirect(url_for('inserzionista', id_utente=user.id_utente))
        else:
            flash("Email o password sbagliata", category="alert alert-warning")
            return redirect(url_for('log'))

    return render_template('login.html')
    
## logout

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    session.pop('role', None)
    flash("Logout effettuato con successo", category='alert alert-success')
    return redirect(url_for('log'))

## registrazione

@app.route('/registrazione', methods=['GET', 'POST'])
def addprofile():
    if request.method == "POST":
        details = request.form
        username = details['username']
        nome = details['nome']
        cognome = details['cognome']
        password = details['password']
        cpassword = details['cpassword']
        email = details['email']
        sesso = details['sesso']
        eta = details['eta']
        ruolo = details['ruolo']

        if password != cpassword:
            flash("Le password non corrispondono", category="alert alert-warning")
            return render_template('registrazione.html')

        if check_email(email):
            flash("Email non valida", category="alert alert-warning")
            return render_template('registrazione.html')

        if check_password(password):
            flash("Password non valida", category="alert alert-warning")
            return render_template('registrazione.html')

        try:
            user = Users(
                username=username,
                nome=nome,
                cognome=cognome,
                password_=password,  # Assuming you have a mechanism to hash passwords
                email=email,
                sesso=sesso,
                eta=eta,
                ruolo=ruolo
            )
            db.session.add(user)
            db.session.commit()
            flash("Registrazione riuscita", category="alert alert-success")
            # Store the username in the session
            session['new_user'] = username
            # Redirect to the interests selection page
            return redirect(url_for('interessi'))
        except IntegrityError:
            db.session.rollback()
            flash("ERROR: Utente già registrato", category="alert alert-warning")
            return render_template('registrazione.html')

    return render_template('registrazione.html')

## aggiunta interessi

@app.route('/interessi', methods=['GET', 'POST'])
def interessi():
    if request.method == "GET":
        return render_template('interessi.html')
    else:  # if POST
        details = request.form
        interessi_nomi = details.getlist('interessi')

        try:
            # Recupera il nome utente dalla sessione
            username = session.get('new_user')
            if not username:
                flash("Errore: Nessun utente trovato. Per favore, registra prima un account.", category="alert alert-warning")
                return redirect(url_for('registrazione'))
            
            # Recupera l'ID dell'utente usando il nome utente
            user = Users.query.filter_by(username=username).first()
            if not user:
                flash("Errore: Utente non trovato.", category="alert alert-warning")
                return redirect(url_for('registrazione'))

            user_id = user.id_utente
            
            # Rimuovi tutti gli interessi esistenti per l'utente
            UserInteressi.query.filter_by(utente_id=user_id).delete()

            for nome_interesse in interessi_nomi:
                interesse = Interessi.query.filter_by(nome=nome_interesse).first()
                if interesse:
                    user_interesse = UserInteressi(utente_id=user_id, id_interessi=interesse.id_interessi)
                    db.session.add(user_interesse)
            db.session.commit()
            flash("Interessi aggiunti correttamente", category="alert alert-success")
        except IntegrityError:
            db.session.rollback()
            flash("Errore nell'aggiunta degli interessi", category="alert alert-warning")
            return render_template('interessi.html')

        # Redirect to the login page after adding interests
        return redirect(url_for('log'))

#------------------------------------------- home page sito ---------------------------------#

    ## home page utente

@app.route('/homepage/utente/<int:id_utente>', methods=['GET', 'POST'])
@login_required
def utente(id_utente):
    # Recupera l'utente con l'ID passato come parametro
    user = Users.query.filter_by(id_utente=id_utente).first()

    # Verifica se l'utente esiste
    if not user:
        flash("Utente non trovato", category="alert alert-danger")
        return redirect(url_for('log'))

    # Recupera l'ID dell'utente corrente
    current_user_id = current_user.id_utente

    # Recupera gli utenti seguiti dall'utente corrente
    seguiti_ids = [amico.user_amico for amico in Amici.query.filter_by(io_utente=current_user_id).all()]

    # Aggiungi l'ID dell'utente corrente alla lista degli utenti seguiti se necessario
    seguiti_ids.append(current_user_id)

    # Recupera i post degli utenti seguiti
    posts = Post.query.filter(Post.utente.in_(seguiti_ids)).order_by(Post.data_creazione.desc()).all()

    # Recupera gli utenti seguiti in una sola query
    utenti_dict = {utente.id_utente: utente.username for utente in Users.query.filter(Users.id_utente.in_(seguiti_ids)).all()}

    # Recupera gli interessi dell'utente corrente
    interessi_utenti = UserInteressi.query.filter_by(utente_id=current_user_id).all()
    interessi_ids = [interesse.id_interessi for interesse in interessi_utenti]

    # Recupera gli annunci che corrispondono agli interessi e ai target dell'utente
    now = datetime.now()
    annunci = Annunci.query.filter(
        (Annunci.interesse_target.in_(interessi_ids) | (Annunci.interesse_target.is_(None))),  # Corrispondenza degli interessi
        ((Annunci.sesso_target == user.sesso) | (Annunci.sesso_target == 'tutti')),  # Corrispondenza del sesso
        (Annunci.eta_target <= user.eta),  # Età dell'utente deve essere minore o uguale a quella target dell'annuncio
        Annunci.fine > now
    ).order_by(Annunci.fine.desc()).all()

    # Funzione per ottenere il tempo passato
    def get_time_ago(timestamp):
        if timestamp is None:
            return "Data non disponibile"
        return humanize.naturaltime(now - timestamp)

    # Aggiungi il tempo relativo ai post e agli annunci
    for post in posts:
        post.time_ago = get_time_ago(post.data_creazione)

    for annuncio in annunci:
        annuncio.time_ago = get_time_ago(annuncio.data_creazione)

    return render_template('home_utente.html', user=user, posts=posts, utenti=utenti_dict, annunci=annunci)
    
    ## home page inserzionista

@app.route('/homepage/inserzionista/<int:id_utente>', methods=['GET', 'POST'])
@login_required
def inserzionista(id_utente):
    # Recupera l'utente inserzionista
    user = Users.query.filter_by(id_utente=id_utente).first()
    
    # Recupera l'ID dell'utente corrente (chi sta visualizzando la pagina)
    current_user_id = current_user.id_utente
    
    # Recupera gli utenti seguiti dall'utente corrente
    seguiti_ids = [amico.user_amico for amico in Amici.query.filter_by(io_utente=current_user_id).all()]
    
    # Aggiungi l'ID dell'utente corrente alla lista degli utenti seguiti se necessario
    seguiti_ids.append(current_user_id)
    
    # Recupera i post degli utenti seguiti
    posts = Post.query.filter(Post.utente.in_(seguiti_ids)).order_by(Post.data_creazione.desc()).all()
    
    # Recupera gli utenti seguiti in una sola query
    utenti_dict = {utente.id_utente: utente.username for utente in Users.query.filter(Users.id_utente.in_(seguiti_ids)).all()}
    
    # Recupera gli interessi dell'utente corrente
    interessi_utenti = UserInteressi.query.filter_by(utente_id=current_user_id).all()
    interessi_ids = [interesse.id_interessi for interesse in interessi_utenti]
    
    # Recupera gli annunci creati dall'utente corrente
    now = datetime.now()
    annunci = Annunci.query.filter(
        Annunci.advertiser_id == current_user_id,
        Annunci.fine > now
    ).order_by(Annunci.inizio.desc()).all()
    
    # Recupera gli utenti che hanno creato gli annunci
    inserzionisti = {annuncio.id: Users.query.filter_by(id_utente=annuncio.advertiser_id).first() for annuncio in annunci}
    
    # Recupera statistiche per ogni annuncio
    statistiche_annunci = {
        annuncio.id: recupera_statistiche_annuncio(annuncio.id) for annuncio in annunci
    }
    
    return render_template('home_inserzionista.html', user=user, posts=posts, utenti_dict=utenti_dict, annunci=annunci, statistiche=statistiche_annunci, inserzionisti=inserzionisti)


#--------------------------------------- pagina profilo utente e inserzionista ----------------------------------#
    ## pagina profilo utente

@app.route('/profilo', methods=['GET', 'POST'])
@login_required
def profilo():
    # Recupera l'utente corrente
    user = current_user
    posts = Post.query.filter_by(utente=user.id_utente).all()
    
    return render_template('profilo_io.html', user=user, posts=posts)

    ## modificare il profilo

@app.route('/modifica', methods=['GET', 'POST'])
@login_required
def modifica_profilo():
    user = Users.query.get(current_user.id_utente)  # Assumi che current_user abbia l'id_utente
    interessi = Interessi.query.all()  # Retrieve all available interests

    if request.method == 'POST':
        # Gestione della richiesta POST
        username = request.form.get('username')
        nome = request.form.get('nome')
        cognome = request.form.get('cognome')
        email = request.form.get('email')
        sesso = request.form.get('sesso')
        eta = request.form.get('eta')
        ruolo = request.form.get('ruolo')
        bio = request.form.get('bio')
        immagine = request.files.get('immagine')
        interessi_selezionati = request.form.getlist('interessi')

        if not all([username, nome, cognome, email, sesso, eta, ruolo]):
            
            return redirect(url_for('modifica_profilo'))

        existing_user = Users.query.filter_by(username=username).first()
        if existing_user and existing_user.id_utente != current_user.id_utente:
            flash('Username giÃ  in uso.', 'alert alert-danger')
            return redirect(url_for('modifica_profilo'))

        if user:
            user.username = username
            user.nome = nome
            user.cognome = cognome
            user.email = email
            user.sesso = sesso
            user.eta = eta
            user.ruolo = ruolo
            user.bio = bio

            if immagine and allowed_file(immagine.filename):
                filename = secure_filename(immagine.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                immagine.save(filepath)
                user.immagine = filename

            # Update user interests
            UserInteressi.query.filter_by(utente_id=user.id_utente).delete()  # Remove all current interests
            for interesse_id in interessi_selezionati:
                user_interesse = UserInteressi(utente_id=user.id_utente, id_interessi=interesse_id)
                db.session.add(user_interesse)

            db.session.commit()

        return redirect(url_for('profilo'))

    # Retrieve current user interests for display in the form
    user_interessi = [ui.id_interessi for ui in UserInteressi.query.filter_by(utente_id=user.id_utente).all()]

    return render_template('modifica_profilo.html', user=user, interessi=interessi, user_interessi=user_interessi)


## pagina profilo inserzionista

#------------------------------ pubblicazione post -------------------------------#

    ## scelta di cosa pubblicare

@app.route('/scegli_post', methods=['GET', 'POST'])
def scegli_post():
    user = current_user
    
    is_pubblicitario = current_user.is_pubblicitario  # Adatta a seconda della tua logica
    
    return render_template('scelta_post.html',is_pubblicitario=is_pubblicitario)

    ## pubblicazione testo
 
@app.route('/pubblica_testo', methods=['GET', 'POST'])
@login_required
def pubblica_testo():
    if request.method == 'POST':
        testo = request.form['testo']
        nuovo_post = Post(utente=current_user.id_utente, tipo_post='testo', testo=testo)
        db.session.add(nuovo_post)
        db.session.commit()
        return redirect(url_for('utente', id_utente=current_user.id_utente))
    return render_template('pubblicazione_testo.html')

    ## pubblicazione video

@app.route('/pubblica_video', methods=['GET', 'POST'])
@login_required
def pubblica_video():
    if request.method == 'POST':
        video = request.files['video']
        testo = request.form['testo']
        nome_file = 'contenuti' + video.filename  # Modificare il percorso per salvare il video
        video.save(nome_file)
        nuovo_post = Post(utente=current_user.id_utente, tipo_post='video', testo=testo, media=nome_file)
        db.session.add(nuovo_post)
        db.session.commit()
        return redirect(url_for('utente', id_utente=current_user.id_utente))
    return render_template('pubblicazione_video.html')

    ## pubblicazione immagine

@app.route('/pubblica_immagini', methods=['GET', 'POST'])
@login_required
def pubblica_immagini():
    if request.method == 'POST':
        immagine = request.files['immagine']
        testo = request.form['testo']
        
        # Ensure the 'contenuti' directory exists
        contenuti_path = os.path.join(current_app.root_path, 'contenuti')
        if not os.path.exists(contenuti_path):
            os.makedirs(contenuti_path)
        
        # Construct the full file path
        nome_file = os.path.join(contenuti_path, immagine.filename)
        
        # Save the image to the 'contenuti' directory
        immagine.save(nome_file)
        
        # Create a new post entry in the database
        nuovo_post = Post(utente=current_user.id_utente, tipo_post='immagini', testo=testo, media=immagine.filename)
        db.session.add(nuovo_post)
        db.session.commit()
        
        return redirect(url_for('utente', id_utente=current_user.id_utente))
    
    return render_template('pubblicazione_immagine.html')

@app.route('/contenuti/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#------------------------------ vedere i post ed eliminarli -------------------------------#

## vedere post

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_details(post_id):
    post = Post.query.get_or_404(post_id)
    post_user = Users.query.get_or_404(post.utente)
    comments = PostComments.query.filter_by(post_id=post_id).all()

    comment_users = {}
    for comment in comments:
        comment_user = Users.query.get(comment.utente_id)
        if comment_user:
            comment_users[comment.id] = comment_user

    liked = PostLikes.query.filter_by(post_id=post_id, utente_id=current_user.id_utente).first() is not None

    # Fetch the user's friends
    friends = db.session.query(Users).join(Amici, Amici.user_amico == Users.id_utente).filter(Amici.io_utente == current_user.id_utente).all()

    if request.method == 'POST':
        if 'content' in request.form:
            content = request.form['content']
            new_comment = PostComments(post_id=post_id, utente_id=current_user.id_utente, content=content)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('post_details', post_id=post_id))

    return render_template('post.html', post=post, post_user=post_user, comments=comments, comment_users=comment_users, liked=liked, friends=friends)
    
## eliminare post

@app.route('/elimina_post/<int:post_id>', methods=['POST'])
@login_required
def elimina_post(post_id):
    # Recupera il post con l'ID specificato
    post = Post.query.get_or_404(post_id)
    # Verifica se l'utente corrente Ã¨ l'autore del post
    if post.utente != current_user.id_utente:
        flash("Non sei autorizzato a eliminare questo post.", category="alert alert-danger")
        return redirect(url_for('utente', id_utente=current_user.id_utente))
    # Elimina i like associati al post
    PostLikes.query.filter_by(post_id=post_id).delete()
    # Elimina il post
    db.session.delete(post)
    db.session.commit()
    flash("Post eliminato con successo.", category="alert alert-success")
    return redirect(url_for('utente', id_utente=current_user.id_utente))

## condividere post

@app.route('/share_post/<int:post_id>/<int:friend_id>', methods=['POST'])
def share_post(post_id, friend_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    additional_text = request.form.get('additional_text')
    if additional_text:
        new_message = Messaggi(
            testo=additional_text,
            mittente_id=current_user.id_utente,
            destinatario_id=friend_id,
            postinviato=post_id
        )
        db.session.add(new_message)
        db.session.commit()

    return redirect(url_for('chat', other_user_id=friend_id))


#------------------------------ inserire ed eliminare commenti -------------------------------#

## inserimento commenti

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form['content']
    user_id = 1  # Get the currently logged-in user ID
    new_comment = PostComments(post_id=post_id, utente_id=user_id, content=content)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('post_details', post_id=post_id))

## eliminare commenti

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = PostComments.query.get(comment_id)
    if comment is None:
        flash('Commento non trovato.', 'danger')
        return redirect(url_for('post_details', post_id=comment.post_id))

    if comment.utente_id != current_user.id_utente and comment.post.utente != current_user.id_utente:
        flash('Non hai il permesso per eliminare questo commento.', 'danger')
        return redirect(url_for('post_details', post_id=comment.post_id))

    db.session.delete(comment)
    db.session.commit()
    flash('Commento eliminato con successo.', 'success')
    return redirect(url_for('post_details', post_id=comment.post_id))


#------------------------------ mettere e togliere mi piace -------------------------------#

@app.route('/toggle_like/<int:post_id>', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    like = PostLikes.query.filter_by(post_id=post.id, utente_id=current_user.id_utente).first()
    
    if like:
        # Se esiste un like, rimuovilo (dislike)
        db.session.delete(like)
        db.session.commit()
    else:
        # Altrimenti, aggiungi un nuovo like
        new_like = PostLikes(post_id=post.id, utente_id=current_user.id_utente)
        db.session.add(new_like)
        db.session.commit()

    return redirect(url_for('post_details', post_id=post.id))

#------------------------------ Notifiche -------------------------------#

@app.route('/notifiche', methods=['GET'])
@login_required
def notifiche():
    user_id = current_user.id_utente

    # Recuperare i like ricevuti
    like_notifiche = db.session.query(PostLikes, Post, Users)\
        .join(Post, PostLikes.post_id == Post.id)\
        .join(Users, PostLikes.utente_id == Users.id_utente)\
        .filter(Post.utente == user_id)\
        .filter(PostLikes.utente_id != user_id)\
        .all()

    # Recuperare i commenti ricevuti
    comment_notifiche = db.session.query(PostComments, Post, Users)\
        .join(Post, PostComments.post_id == Post.id)\
        .join(Users, PostComments.utente_id == Users.id_utente)\
        .filter(Post.utente == user_id)\
        .filter(PostComments.utente_id != user_id)\
        .all()

    # Recuperare le richieste di amicizia
    friend_requests = db.session.query(Amici, Users)\
        .join(Users, Amici.io_utente == Users.id_utente)\
        .filter(Amici.user_amico == user_id)\
        .all()

    # Creare una lista di notifiche combinata
    all_notifications = []

    # Aggiungere le notifiche di like
    for post_like, post, user in like_notifiche:
        all_notifications.append({
            'type': 'like',
            'user': user,
            'post': post,
            'timestamp': post_like.clicked_at,
            'time_ago': time_since(post_like.clicked_at)
        })

    # Aggiungere le notifiche di commento
    for comment, post, user in comment_notifiche:
        all_notifications.append({
            'type': 'comment',
            'user': user,
            'post': post,
            'comment': comment,
            'timestamp': comment.created_at,
            'time_ago': time_since(comment.created_at)
        })

    # Aggiungere le notifiche di nuovi follower
    for follower, user in friend_requests:
        all_notifications.append({
            'type': 'follower',
            'user': user,
            'timestamp': follower.seguito_at,
            'time_ago': time_since(follower.seguito_at)
        })

    # Ordinare le notifiche per data
    all_notifications.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template('notifiche.html', all_notifications=all_notifications)

## funzione per l'orario di arrivo delle notifiche

def time_since(post_time):
    # Definire il fuso orario italiano
    italian_tz = pytz.timezone('Europe/Rome')

    # Assicurarsi che 'post_time' sia timezone-aware e sia nel fuso orario italiano
    if post_time.tzinfo is None:
        post_time = italian_tz.localize(post_time)  # Localizza il tempo a Italia

    now = datetime.now(italian_tz)  # Ottieni l'orario corrente in Italia
    diff = now - post_time

    if diff.days > 0:
        return f"{diff.days} giorni fa"
    elif diff.seconds // 3600 > 0:
        return f"{diff.seconds // 3600} ore fa"
    elif diff.seconds // 60 > 0:
        return f"{diff.seconds // 60} minuti fa"
    else:
        return "ora"

#------------------------------ ricerca utente e visualizzazione profilo -------------------------------#

## ricerca utente

@app.route('/search_suggestions')
@login_required
def search_suggestions():
    query = request.args.get('q')
    if not query:
        return jsonify({'suggestions': []})

    suggestions = db.session.query(Users).filter(Users.username.ilike(f'%{query}%')).limit(10).all()
    
    return jsonify({
        'suggestions': [{'id': user.id_utente, 'username': user.username} for user in suggestions]
    })

## visualizzazione profilo

@app.route('/profilo_amico/<int:id_amico>', methods=['GET', 'POST'])
@login_required
def profilo_amico(id_amico):
    amico = Users.query.get(id_amico)
    if not amico:
        return "Utente non trovato", 404

    amicizia = Amici.query.filter_by(io_utente=current_user.id_utente, user_amico=id_amico).first()

    if request.method == 'POST':
        if amicizia:
            # Se l'amicizia esiste, togli la connessione
            db.session.delete(amicizia)
        else:
            # Altrimenti, crea una nuova amicizia
            amicizia = Amici(io_utente=current_user.id_utente, user_amico=id_amico)
            db.session.add(amicizia)
        db.session.commit()
        return redirect(url_for('profilo_amico', id_amico=id_amico))

    # Recupera i post solo se si segue l'utente
    posts = []
    if amicizia:
        posts = Post.query.filter_by(utente=id_amico).all()

    return render_template('profilo_amico.html', amico=amico, seguendo=amicizia is not None, posts=posts)

#------------------------------- FOLLOWER, SEGUITI, E RIMUOVERE AMICI/SEGUITI ---------------------------------#

    ## vedere elenco follower

@app.route('/lista_follower/<int:user_id>')
@login_required
def followers_list(user_id):
    if user_id != current_user.id_utente:
        abort(403)  # Forbidden access

    followers = db.session.query(Users).join(Amici, Amici.io_utente == Users.id_utente).filter(Amici.user_amico == user_id).all()
    return render_template('lista_follower.html', followers=followers)

## vedere elenco seguiti

@app.route('/lista_seguiti/<int:user_id>')
@login_required
def following_list(user_id):
    if user_id != current_user.id_utente:
        abort(403)  # Forbidden access

    following = db.session.query(Users).join(Amici, Amici.user_amico == Users.id_utente).filter(Amici.io_utente == user_id).all()
    return render_template('lista_seguiti.html', following=following)

## poter unfolloware una persona dall'elenco

@app.route('/unfollow/<int:id_amico>', methods=['POST'])
@login_required
def unfollow(id_amico):
    # Ottieni l'utente corrente
    user_id = current_user.id_utente

    # Trova la relazione di amicizia che deve essere rimossa
    amicizia = Amici.query.filter_by(io_utente=user_id, user_amico=id_amico).first()
    
    if amicizia:
        # Rimuovi la relazione di amicizia
        db.session.delete(amicizia)
        db.session.commit()
        flash('Non segui più questa persona.', 'success')
    else:
        flash('Impossibile trovare l\'amicizia da rimuovere.', 'error')

    return redirect(url_for('following_list', user_id=user_id))  # Redirige alla pagina dei seguiti

## poter togliere un follower dall'elenco

@app.route('/remove_follower/<int:id_follower>', methods=['POST'])
@login_required
def remove_follower(id_follower):
    # Ottieni l'utente corrente
    user_id = current_user.id_utente

    # Trova la relazione di amicizia che deve essere rimossa
    follower_relation = Amici.query.filter_by(io_utente=id_follower, user_amico=user_id).first()
    
    if follower_relation:
        # Rimuovi la relazione di amicizia
        db.session.delete(follower_relation)
        db.session.commit()
        flash('Follower rimosso con successo.', 'success')
    else:
        flash('Impossibile trovare il follower da rimuovere.', 'error')

    # Redirigi alla pagina dei follower per l'utente corrente
    return redirect(url_for('followers_list', user_id=user_id))

#------------------------------- chat tra amici ---------------------------------#

## elenco delle conversazioni

@app.route('/conversations')
def conversations():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    current_user_id = current_user.id_utente

    # Fetch conversations involving the current user
    messages = db.session.query(Messaggi).filter(
        (Messaggi.mittente_id == current_user_id) | (Messaggi.destinatario_id == current_user_id)
    ).order_by(Messaggi.creato_at.desc()).all()

    # Organize messages by conversation
    conversations = {}
    for msg in messages:
        other_user_id = msg.destinatario_id if msg.mittente_id == current_user_id else msg.mittente_id
        if other_user_id not in conversations:
            conversations[other_user_id] = []
        conversations[other_user_id].append(msg)

    # Fetch user details
    user_ids = set(user_id for user_id in conversations.keys()) | {current_user_id}
    users = {user.id_utente: user for user in db.session.query(Users).filter(Users.id_utente.in_(user_ids)).all()}

    return render_template('conversations.html', conversations=conversations, users=users)

## chat tra amici

@app.route('/chat/<int:other_user_id>', methods=['GET', 'POST'])
def chat(other_user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    current_user_id = current_user.id_utente

    # Fetch all messages between the current user and the specified user
    messages = db.session.query(Messaggi).filter(
        ((Messaggi.mittente_id == current_user_id) & (Messaggi.destinatario_id == other_user_id)) |
        ((Messaggi.mittente_id == other_user_id) & (Messaggi.destinatario_id == current_user_id))
    ).order_by(Messaggi.creato_at.asc()).all()

    if request.method == 'POST':
        # Handle new message
        message_text = request.form.get('message')
        postinviato = request.form.get('postinviato', None)
        additional_text = request.form.get('additional_text')  # Fetch the additional text

        if message_text or postinviato or additional_text:
            new_message = Messaggi(
                testo=message_text if message_text else additional_text,  # Prioritize message_text if present
                mittente_id=current_user_id,
                destinatario_id=other_user_id,
                postinviato=postinviato  # Include post ID if present
            )
            db.session.add(new_message)
            db.session.commit()
            return redirect(url_for('chat', other_user_id=other_user_id))

    # Fetch user details for the chat partner
    user = db.session.query(Users).get(other_user_id)
    if not user:
        abort(404)  # User not found, handle accordingly

    # Fetch all users to pass to the template for username resolution
    all_users = db.session.query(Users).all()
    users = {u.id_utente: u for u in all_users}

    # Fetch all posts to pass to the template for post resolution
    all_posts = db.session.query(Post).all()
    posts = {p.id: p for p in all_posts}

    return render_template('chat.html', messages=messages, user=user, users=users, posts=posts, other_user_id=other_user_id)


@app.route('/send_message/<int:other_user_id>', methods=['POST'])
def send_message(other_user_id):
    # Your logic to handle sending the message
    message_text = request.form.get('message')
    # Create and save the new message to the database
    new_message = Messaggi(testo=message_text, mittente_id=current_user.id_utente, destinatario_id=other_user_id, postinviato=None)
    db.session.add(new_message)
    db.session.commit()
    return redirect(url_for('chat', user_id=other_user_id))


#------------------------------- Annunci ---------------------------------#

##pubblicare annuncio

@app.route('/pubblica_annuncio', methods=['GET', 'POST'])
@login_required
def pubblica_annuncio():
    if request.method == 'POST':
        user_id = current_user.id_utente
        tipo_post = request.form['tipo_post']
        sesso_target = request.form['sesso_target']
        eta_target = int(request.form['eta_target'])
        nome_interesse = request.form['nome_interesse']
        durata_annuncio = int(request.form['durata_annuncio'])
        titolo = request.form.get('titolo')
        didascalia = request.form.get('didascalia')

        if tipo_post == 'immagini':
            immagine = request.files['immagine']
            testo = None
        elif tipo_post == 'testo':
            immagine = None
            testo = request.form.get('testo')
        else:
            return "Tipo di post non valido."

        # Assicurati che la directory 'contenuti' esista
        # Ensure the 'contenuti' directory exists
        contenuti_path = os.path.join(current_app.root_path, 'contenuti')
        if not os.path.exists(contenuti_path):
            os.makedirs(contenuti_path)
        
        # Construct the full file path
        nome_file = os.path.join(contenuti_path, immagine.filename)
        
        # Save the image to the 'contenuti' directory
        immagine.save(nome_file)

        try:
            # Crea il nuovo annuncio
            annuncio = crea_annuncio(
                user_id=user_id,
                tipo_post=tipo_post,
                sesso_target=sesso_target,
                eta_target=eta_target,
                nome_interesse=nome_interesse,
                durata_annuncio=durata_annuncio,
                testo=testo,
                titolo=titolo,
                didascalia=didascalia,
                media=immagine  # Aggiungi il nome del file come media nel database
            )
            
            if isinstance(annuncio, str):
                return f"Errore: {annuncio}"
            
            # Reindirizza alla home dell'inserzionista con un messaggio di successo
            return redirect(url_for('inserzionista', id_utente=user_id))
        
        except IntegrityError:
            db.session.rollback()
            return "Errore di integrità del database."
        except Exception as e:
            db.session.rollback()
            return f"Errore: {str(e)}"
    
    interests = Interessi.query.all()
    return render_template('pubblica_annuncio.html', message=None, interests=interests)
## annunci dedicati all'utente

def recupera_annunci_utente(current_user_id):
    now = datetime.now()
    
    # Recupera l'utente corrente
    current_user = Users.query.get(current_user_id)
    
    # Recupera gli interessi dell'utente corrente
    interessi_utenti = UserInteressi.query.filter_by(utente_id=current_user_id).all()
    interessi_ids = [interesse.id_interessi for interesse in interessi_utenti]

    # Recupera gli annunci che non sono scaduti e che sono destinati all'utente corrente
    annunci = Annunci.query.filter(
        (Annunci.interesse_target.in_(interessi_ids) | (Annunci.interesse_target.is_(None))),  # Annunci con interessi che corrispondono o senza target specificato
        ((Annunci.sesso_target == current_user.sesso) | (Annunci.sesso_target == 'tutti')),  # Corrispondenza del sesso
        (Annunci.eta_target >= current_user.eta),
        Annunci.fine > now
    ).order_by(Annunci.fine.desc()).all()
    
    return annunci

## aggiungi commenti

@app.route('/annuncio/<int:annuncio_id>/comment', methods=['POST'])
def add_comment_annuncio(annuncio_id):
    # Recupera l'annuncio con l'ID fornito
    annuncio = Annunci.query.get_or_404(annuncio_id)
    
    # Recupera il contenuto del commento dal modulo
    content = request.form.get('content')
    
    # Verifica se il contenuto del commento è vuoto
    if not content:
        flash('Il commento non può essere vuoto.', 'warning')
        return redirect(url_for('post_details', annuncio_id=annuncio_id))
    
    # Recupera l'ID dell'utente loggato
    user_id = current_user.id
    
    # Crea una nuova istanza di AnnunciComments
    new_comment = AnnunciComments(annuncio_id=annuncio_id, utente_id=user_id, content=content)
    
    # Aggiungi il nuovo commento al database e committi
    db.session.add(new_comment)
    db.session.commit()
    
    # Reindirizza alla pagina dei dettagli dell'annuncio
    return redirect(url_for('recupera_statistiche_annuncio', annuncio_id=annuncio_id))

## statistiche degli annunci

def recupera_statistiche_annuncio(annuncio_id):
    num_clicks = db.session.query(AnnunciClicks).filter_by(annuncio_id=annuncio_id).count()
    num_comments = db.session.query(AnnunciComments).filter_by(annuncio_id=annuncio_id).count()
    num_likes = db.session.query(AnnunciLikes).filter_by(annuncio_id=annuncio_id).count()
    
    return {
        'clicks': num_clicks,
        'comments': num_comments,
        'likes': num_likes
    }

@app.route('/insight')
@login_required
def insight():
    
    return render_template('insight.html')



# Inizializzazione dell'applicazione
if __name__ == '__main__':
    app.run(debug=True)