from flask import Flask, request, url_for, redirect, render_template, flash, Blueprint, current_app,jsonify, session, send_from_directory
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
from datetime import datetime, timezone
import pytz

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

class Stato(Enum):
    accettato = "accettato"
    in_attesa = "in attesa"
    non_accettato = "non accettato"

class Users(UserMixin, db.Model):
    __tablename__ = 'users'

    id_utente = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    immagine = Column(String(100), nullable=True)
    nome = Column(String(50), unique=False, nullable=False)
    cognome = Column(String(50), unique=False, nullable=False)
    password_hash = Column(String(150), nullable=False)  # Changed to password_hash
    email = Column(String(150), unique=True, nullable=False)
    sesso = Column(SQLAlchemyEnum(Sesso))
    eta = Column(Integer, unique=False, nullable=False)
    ruolo = Column(SQLAlchemyEnum(Ruolo))
    bio = Column(String(250), unique=False, nullable=True)


    def __init__(self,id_utente, username, nome, cognome, password, email, sesso, eta, ruolo, immagine=None, bio=None):
        self.id_utente = id_utente
        self.username = username
        self.immagine = immagine
        self.nome = nome
        self.cognome = cognome
        self.password_hash = password
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
        return self.password_hash == password

    def url_photo(self):
        if self.immagine:
            return '/contenuti/' + self.immagine
        else:
            return None
        
    @property
    def follower_count(self):
        return Amici.query.filter_by(user_amico=self.id_utente, stato=Stato.accettato).count()

    @property
    def following_count(self):
        return Amici.query.filter_by(io_utente=self.id_utente, stato=Stato.accettato).count()

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

    utente = Column(Integer, ForeignKey('users.id_utente'), nullable=False, primary_key=True)
    id_interessi = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False, primary_key=True)

    def __init__(self, utente, id_interessi):
        self.utente = utente
        self.id_interessi = id_interessi

class Amici(db.Model, UserMixin):
    __tablename__ = 'amici'

    io_utente = Column(Integer, ForeignKey('users.id_utente'), nullable=False, primary_key=True)
    user_amico = Column(Integer, ForeignKey('users.id_utente'), nullable=False, primary_key=True)
    stato = Column(SQLAlchemyEnum(Stato), nullable=False)

    def __init__(self, io_utente, user_amico, stato):
        self.io_utente = io_utente
        self.user_amico = user_amico
        self.stato = stato

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
    advertiser = Column(Integer, ForeignKey('users.id_utente'), nullable=False)
    tipo_post = Column(SQLAlchemyEnum('immagini', 'video', 'testo', name='tipo_post'))
    sesso_target = Column(SQLAlchemyEnum(Sesso))
    eta_target = Column(Integer, unique=False, nullable=False)
    interesse_target = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False)
    inizio = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)
    fine = Column(Date, default=func.current_timestamp())

    def __init__(self, advertiser, tipo_post, sesso_target, eta_target, interesse_target, fine):
        self.advertiser = advertiser
        self.tipo_post = tipo_post
        self.sesso_target = sesso_target
        self.eta_target = eta_target
        self.interesse_target = interesse_target
        self.fine = fine

class AnnunciLikes(db.Model, UserMixin):
    __tablename__ = 'annunci_likes'

    annuncio_id = Column(Integer, ForeignKey('annunci.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id_utente'), primary_key=True)  # Modificato in user_id
    clicked_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)

    def __init__(self, annuncio_id, user_id):
        self.annuncio_id = annuncio_id
        self.user_id = user_id

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

#------------------------ rotte sito internet -------------------------#

@app.route('/', methods=['GET', 'POST'])
def log():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    session.pop('role', None)
    flash("Logout effettuato con successo", category='alert alert-success')
    return redirect(url_for('log'))


@app.route('/homepage/utente/<int:id_utente>', methods=['GET', 'POST'])
@login_required
def utente(id_utente):
    # Recupera l'utente con il nome utente passato come parametro
    user = Users.query.filter_by(id_utente=id_utente).first()

    # Verifica se l'utente esiste
    if not user:
        flash("Utente non trovato", category="alert alert-danger")
        return redirect(url_for('log'))

    # Recupera l'ID dell'utente corrente
    current_user_id = current_user.id_utente

    # Recupera gli utenti seguiti dall'utente corrente
    seguiti = [amico.user_amico for amico in Amici.query.filter_by(io_utente=current_user_id, stato=Stato.accettato).all()]

    # Recupera i post degli utenti seguiti
    posts = Post.query.filter(Post.utente.in_(seguiti)).order_by(Post.data_creazione.desc()).all()

    # Recupera gli utenti in una sola query
    utenti = {utente.id_utente: utente.username for utente in Users.query.filter(Users.id_utente.in_(seguiti)).all()}


    return render_template('home_utente.html', user=user, posts=posts, utenti=utenti)


@app.route('/homepage/inserzionista/<username>', methods=['GET', 'POST'])
@login_required
def inserzionista(username):
    user = Users.query.filter_by(username=username).first_or_404()
    return render_template('home_inserzionista.html', user=user)

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
        errore = False

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
                password_hash=password,  # Assuming you have a mechanism to hash passwords
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

@app.route('/interessi', methods=['GET', 'POST'])
def interessi():
    if request.method == "GET":
        return render_template('interessi.html')
    else:  # if POST
        details = request.form
        interessi = details.getlist('interessi')
        errore = False

        try:
            # Retrieve the username from the session
            username = session.get('new_user')
            if not username:
                flash("Errore: Nessun utente trovato. Per favore, registra prima un account.", category="alert alert-warning")
                return redirect(url_for('registrazione'))
            
            for interesse in interessi:
                user_interesse = UserInteressi(utente=username, id_interessi=interesse)
                db.session.add(user_interesse)
            db.session.commit()
            flash("Interessi aggiunti correttamente", category="alert alert-success")
        except IntegrityError:
            db.session.rollback()
            flash("Errore nell'aggiunta degli interessi", category="alert alert-warning")
            return render_template('interessi.html')

        # Redirect to the login page after adding interests
        return redirect(url_for('login.log'))

@app.route('/profilo', methods=['GET', 'POST'])
@login_required
def profilo():
    # Recupera l'utente corrente
    user = current_user
    posts = Post.query.filter_by(utente=user.id_utente).all()
    
    return render_template('profilo_io.html', user=user, posts=posts)

from sqlalchemy.exc import IntegrityError

@app.route('/modifica', methods=['GET', 'POST'])
@login_required
def modifica_profilo():
    user = Users.query.get(current_user.id_utente)  # Assumi che current_user abbia l'id_utente

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

        if not all([username, nome, cognome, email, sesso, eta, ruolo]):
            flash('Tutti i campi sono obbligatori.', 'alert alert-danger')
            return redirect(url_for('modifica_profilo'))

        existing_user = Users.query.filter_by(username=username).first()
        if existing_user and existing_user.id_utente != current_user.id_utente:
            flash('Username già in uso.', 'alert alert-danger')
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

            db.session.commit()
            flash('Profilo aggiornato con successo!', 'alert alert-success')
        else:
            flash('Utente non trovato', 'alert alert-danger')

        return redirect(url_for('profilo'))

    return render_template('modifica_profilo.html', user=user)


@app.route('/contenuti/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


#------------------------------ pubblicazione post -------------------------------#

## pubblicazione testo
 
@app.route('/pubblica/testo/<username>', methods=['POST'])
@login_required
def post_testo(username):
    contenuto = request.form.get('contenuto')
    tipo_post = request.form.get('tipo_post','testo')  # Assume che ci sia un campo 'tipo_post' nel form

    if not contenuto:
        flash('Il post non può essere vuoto', 'alert alert-warning')
        return render_template('pubblicazione_testo.html') # rimane nella stessa pagina html

    nuovo_post = Post(
        utente=current_user.username,
        tipo_post=tipo_post,
        data_creazione=datetime.now(),
        testo=contenuto
    )

    try:
        db.session.add(nuovo_post)
        db.session.commit()
        flash('Post pubblicato con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash('Errore durante la pubblicazione del post: {str(e)}', 'alert alert-danger')

    if current_user.is_inserzionista:
        return render_template('home_inserzionista.html')
    else:
        return render_template('home_utente.html')

## pubblicazione video

@app.route('/pubblica/video/<username>', methods=['POST'])
@login_required
def post_video(username):
    file = request.files.get('video')
    contenuto = request.form.get('contenuto')

    if not file or file.filename == '':
        flash('Nessun file selezionato', 'alert alert-warning')
        return render_template('pubblicazione_video.html')

    filename = secure_filename(file.filename)
    file.save(os.path.join('contenuti', filename))  # Specifica il percorso dove salvare il file

    nuovo_post = Post(
        utente=current_user.username,
        media=filename,
        tipo_post='video',
        data_creazione=datetime.now(),
        testo=contenuto
    )

    try:
        db.session.add(nuovo_post)
        db.session.commit()
        flash('Post di video pubblicato con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante la pubblicazione del post: {str(e)}', 'alert alert-danger')
    
    if current_user.is_inserzionista:
        return render_template('home_inserzionista.html')
    else:
        return render_template('home_utente.html')

## pubblicazione immagine

@app.route('/pubblica/immagine/<username>', methods=['POST'])
@login_required
def post_immagine(username):
    file = request.files.get('photo')
    contenuto = request.form.get('contenuto')

    if not file or file.filename == '':
        flash('Nessun file selezionato', 'alert alert-warning')
        return render_template('pubblicazione_immagine.html')

    filename = secure_filename(file.filename)
    file.save(os.path.join('contenuti', filename))  # Specifica il percorso dove salvare il file

    nuovo_post = Post(
        utente=current_user.username,
        tipo_post='immagine',
        data_creazione=datetime.now(),
        testo=contenuto,
        media=filename
    )

    try:
        db.session.add(nuovo_post)
        db.session.commit()
        flash('Post di immagine pubblicato con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante la pubblicazione del post: {str(e)}', 'alert alert-danger')

    if current_user.is_inserzionista:
        return render_template('home_inserzionista.html')
    else:
        return render_template('home_utente.html')

@app.route('/elimina_post/<int:post_id>', methods=['DELETE'])
@login_required
def elimina_post(id):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se il post esiste e appartiene all'utente corrente
        cursor.execute("SELECT * FROM posts WHERE id = ? AND utente = ?", (id, current_user))
        post = cursor.fetchone()
        
        if post is None:
            return jsonify({"message": "Post non trovato o non autorizzato"}), 404

        # Elimina i commenti associati al post
        cursor.execute("DELETE FROM post_comments WHERE id = ?", (id,))

        # Elimina i like associati al post
        cursor.execute("DELETE FROM post_likes WHERE id = ?", (id,))
        
        # Elimina il post
        cursor.execute("DELETE FROM posts WHERE id = ?", (id,))
        
        conn.commit()
        return jsonify({"message": "Post eliminato con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('profilo_io.html')

#------------------------------ inserimento commenti -------------------------------#

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form['content']
    user_id = 1  # Get the currently logged-in user ID
    new_comment = PostComments(post_id=post_id, utente_id=user_id, content=content)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('post_details', post_id=post_id))

    

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



#------------------------------ inserimento mi piace -------------------------------#

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


@app.route('/mi_piace/<int:post_id>', methods=['POST'])
@login_required
def mi_piace(post_id):
    post = Post.query.get(post_id)

    if not post:
        flash('Il post non esiste', 'alert alert-warning')
        return redirect(url_for('app.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

    if current_user.username == post.autore:
        flash('Non puoi mettere mi piace al tuo stesso post', 'alert alert-warning')
        return redirect(url_for('app.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

    nuovo_like = PostLikes(post_id=post_id, username=current_user.username)

    try:
        db.session.add(nuovo_like)
        db.session.commit()
        flash('Mi piace aggiunto con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'aggiunta del mi piace: {str(e)}', 'alert alert-danger')
    
    return redirect(url_for('app.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

@app.route('/<int:post_id>', methods=['DELETE'])
@login_required
def elimina_mi_piace(post_id):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se il commento esiste e appartiene all'utente corrente
        cursor.execute("SELECT * FROM post_likes WHERE posts_id = ? AND username = ?", (post_id, current_user))
        commento = cursor.fetchone()
        
        if commento is None:
            return jsonify({"message": "Commento non trovato o non autorizzato"}), 404
        
        # Elimina il commento
        cursor.execute("DELETE FROM post_likes WHERE post_id = ?", (post_id))
        
        conn.commit()
        return jsonify({"message": "Like eliminato con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('home_utente.html', user=current_user)

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

    stato = 'in attesa'
    # Recuperare le richieste di amicizia
    friend_requests = db.session.query(Amici, Users)\
        .join(Users, Amici.io_utente == Users.id_utente)\
        .filter(Amici.user_amico == user_id, Amici.stato == stato)\
        .all()

    # Creare una lista di notifiche combinata
    all_notifications = []

    # Aggiungere le notifiche di like
    for post_like, post, user in like_notifiche:
        all_notifications.append({
            'type': 'like',
            'user': user,
            'post': post,
            'time_ago': time_since(post_like.clicked_at)
        })

    # Aggiungere le notifiche di commento
    for comment, post, user in comment_notifiche:
        all_notifications.append({
            'type': 'comment',
            'user': user,
            'post': post,
            'comment': comment,
            'time_ago': time_since(comment.created_at)
        })

    # Ordinare le notifiche per data
    all_notifications.sort(key=lambda x: x['time_ago'], reverse=True)

    # Contare le richieste di amicizia in sospeso
    friend_request_count = len(friend_requests)

    return render_template('notifiche.html', 
                           all_notifications=all_notifications, 
                           friend_request_count=friend_request_count)

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


@app.route('/richieste', methods=['GET'])
@login_required
def richieste():
    user_id = current_user.id_utente

    # Recuperare le richieste di amicizia
    friend_requests = db.session.query(Amici, Users).join(Users, Amici.io_utente == Users.id_utente).filter(Amici.user_amico == user_id, Amici.stato == Stato.in_attesa).all()

    return render_template('richieste.html', friend_requests=friend_requests)

#------------------------------ vedere i post -------------------------------#

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

    # Verifica se l'utente ha messo mi piace al post
    liked = PostLikes.query.filter_by(post_id=post_id, utente_id=current_user.id_utente).first() is not None

    if request.method == 'POST':
        # Aggiungi un nuovo commento
        if 'content' in request.form:
            content = request.form['content']
            new_comment = PostComments(post_id=post_id, utente_id=current_user.id_utente, content=content)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('post_details', post_id=post_id))

    return render_template('post.html', post=post, post_user=post_user, comments=comments, comment_users=comment_users, liked=liked)


#------------------------------ seguire e accettare -------------------------------#

    # inviare una richiesta ad una persona

@app.route('/toggle_follow/<int:user_id>', methods=['POST'])
@login_required
def toggle_follow(user_id):
    user_to_follow = Users.query.get_or_404(user_id)
    existing_relationship = Amici.query.filter_by(io_utente=current_user.id_utente, user_amico=user_id).first()

    # Get the action from the form
    action = request.form.get('action')

    if existing_relationship:
        if action == 'unfollow':
            db.session.delete(existing_relationship)
    else:
        if action == 'follow':
            new_relationship = Amici(io_utente=current_user.id_utente, user_amico=user_id, stato=Stato.accettato.value)
            db.session.add(new_relationship)

    db.session.commit()
    return redirect(request.referrer)








@app.route('/accept_request/<int:user_id>', methods=['POST'])
@login_required
def accept_request(user_id):
    relationship = Amici.query.filter_by(io_utente=user_id, user_amico=current_user.id_utente).first()
    if relationship and relationship.stato.value == Stato.in_attesa.value:
        relationship.stato.value = Stato.accettato.value
        db.session.commit()
    return redirect(request.referrer)




    #rifiuta richiesta

@app.route('/richieste/<string:utente>', methods=['POST'])
@login_required
def rifiuta_richiesta(utente):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Aggiorna lo stato della richiesta di amicizia
        cursor.execute("""
            DELETE FROM amici 
            WHERE stato= ? AND user_amico= ? AND io_utente=?
        """, ('in attesa', utente, current_user))
        
        if cursor.rowcount == 0:
            return jsonify({"message": "Errore: richiesta di amicizia non trovata o già accettata"}), 400
        
        conn.commit()
        return jsonify({"message": "Richiesta di amicizia rifiutata con successo :) "}), 200

    except sqlite3.Error as e:
        return jsonify({"message": "Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('profilo_amico.html', user=utente)


#------------------------------ ricerca utente -------------------------------#

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

@app.route('/profilo_amico/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profilo_amico(user_id):
    user = Users.query.get_or_404(user_id)
    relationship = Amici.query.filter_by(io_utente=current_user.id_utente, user_amico=user_id).first()
    posts = Post.query.filter_by(utente=user_id).all()
    return render_template('profile.html', user=user, relationship=relationship, posts=posts, Stato=Stato)

#------------------------------- rimuovere amici ---------------------------------#

    # funzione per rimuovere persone dalle persone che ti seguono

@app.route('/rimuovi_follower/<string:follower>', methods=['DELETE'])
@login_required
def rimuovi_follower(follower):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se il follower esiste e sta seguendo l'utente corrente
        cursor.execute("""
            SELECT * FROM amici WHERE user_amico = ? AND io_utente = ?
        """, (current_user, follower))
        follow = cursor.fetchone()
        
        if follow is None:
            return jsonify({"message": "Follower non trovato"}), 404

        # Rimuovi il follower
        cursor.execute("""
            DELETE FROM amici WHERE user_amico = ? AND io_utente = ?
        """, (follower, current_user))
        
        conn.commit()
        return jsonify({"message": "Follower rimosso con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('lista_amici.html', user=current_user)

    # funzione per smettere di seguire persone

@app.route('/smetti_di_seguire/<string:followed>', methods=['DELETE'])
@login_required
def smetti_di_seguire(follower):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se l'utente corrente sta seguendo la persona specificata
        cursor.execute("""
            SELECT * FROM amici WHERE user_amico = ? AND io_utente = ?
        """, (follower, current_user))
        follow = cursor.fetchone()
        
        if follow is None:
            return jsonify({"message": "Non stai seguendo questa persona"}), 404

        # Smetti di seguire la persona
        cursor.execute("""
            DELETE FROM amici WHERE user_amico = ? AND io_utente = ?
        """, (follower, current_user))
        
        conn.commit()
        return jsonify({"message": "Hai smesso di seguire questa persona"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('profilo_amico.html', user=follower)


# Inizializzazione dell'applicazione
if __name__ == '__main__':
    app.run(debug=True)
