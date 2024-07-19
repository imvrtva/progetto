from flask import Flask, request, url_for, redirect, render_template, flash, Blueprint, current_app,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, BLOB, ForeignKey, TIMESTAMP, Date, func
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
import os
import re
from enum import Enum
from sqlalchemy.types import Enum as SQLAlchemyEnum
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'stringasegreta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ciao@localhost:5433/progettobasi'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login.log'
login_manager.init_app(app)
bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(username):
    return Users.query.filter_by(username=username).first()

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

    username = Column(String(50), unique=True, nullable=False, primary_key=True)
    immagine = Column(BLOB, nullable=True)
    nome = Column(String(50), unique=False, nullable=False)
    cognome = Column(String(50), unique=False, nullable=False)
    password_hash = Column(String(150), nullable=False)  # Changed to password_hash
    email = Column(String(150), unique=True, nullable=False)
    sesso = Column(SQLAlchemyEnum(Sesso))
    eta = Column(Integer, unique=False, nullable=False)
    ruolo = Column(SQLAlchemyEnum(Ruolo))


    def __init__(self, username, nome, cognome, password, email, sesso, eta, ruolo, immagine=None):
        self.username = username
        self.immagine = immagine
        self.nome = nome
        self.cognome = cognome
        self.password_hash = password
        self.email = email
        self.sesso = sesso
        self.eta = eta
        self.ruolo = ruolo

    # Property for password handling
    def get_id(self):
        return self.username

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

class Interessi(db.Model, UserMixin):
    __tablename__ = 'interessi'

    id_interessi = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), unique=False, nullable=False)

    def __init__(self, id_interessi , nome):
        self.id_interessi= id_interessi
        self.nome = nome

class UserInteressi(db.Model, UserMixin):
    __tablename__ = 'user_interessi'

    utente = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    id_interessi = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False, primary_key=True)

    def __init__(self, utente, id_interessi):
        self.utente = utente
        self.id_interessi = id_interessi

class Amici(db.Model, UserMixin):
    __tablename__ = 'amici'

    io_utente = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    user_amico = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    stato = Column(SQLAlchemyEnum(Stato))

    def __init__(self, io_utente, user_amico, stato):
        self.io_utente = io_utente
        self.user_amico = user_amico
        self.stato = stato

class Post(db.Model, UserMixin):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    utente = Column(String(50), ForeignKey('users.username'), nullable=False)
    media = Column(BLOB, nullable=True)
    tipo_post = Column(SQLAlchemyEnum('immagini', 'video', 'testo', name='tipo_post'))
    data_creazione = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    testo = Column(Text, nullable=True)

    def __init__(self, utente, tipo_post, testo=None, media=None):
        self.utente = utente
        self.tipo_post = tipo_post
        self.testo = testo
        self.media = media

    def url_photo(self):
        return '/contenuti/' + self.cover_picture

class PostComments(db.Model, UserMixin):
    __tablename__ = 'post_comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    utentec = Column(String(50), ForeignKey('users.username'), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    def __init__(self, post_id, utentec, content=None):
        self.post_id = post_id
        self.utentec = utentec
        self.content = content

class PostLikes(db.Model, UserMixin):
    __tablename__ = 'post_likes'

    post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey('users.username'), primary_key=True, nullable=False)
    content = Column(Text, nullable=True)
    clicked_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    def __init__(self, post_id, username, content=None):
        self.post_id = post_id
        self.username = username
        self.content = content

class Annunci(db.Model, UserMixin):
    __tablename__ = 'annunci'

    id = Column(Integer, primary_key=True, autoincrement=True)
    advertiser = Column(String(50), ForeignKey('users.username'), nullable=False)
    tipo_post = Column(SQLAlchemyEnum('immagini', 'video', 'testo', name='tipo_post'))
    sesso_target = Column(SQLAlchemyEnum(Sesso))
    eta_target = Column(Integer, unique=False, nullable=False)
    interesse_target = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False)
    inizio = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
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

    annuncio_id = Column(Integer, ForeignKey('annunci.id'), primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey('users.username'), primary_key=True, nullable=False)
    clicked_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    def __init__(self, annuncio_id, username):
        self.annuncio_id = annuncio_id
        self.username = username

# Ensure all tables are created within the application context
with app.app_context():
    db.create_all()

#------------------------ funzioni utili -------------------------#


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
        if user:
            if user.verify_password(password):
                login_user(user)
                if user.ruolo == Ruolo.utente:
                    return redirect(url_for('utente', username=user.username))
                elif user.ruolo == Ruolo.pubblicitari:
                    return redirect(url_for('inserzionista', username=user.username))
            else:
                flash("Password sbagliata", category="alert alert-warning")
                return redirect(url_for('log'))
        else:
            flash("Questa email non è registrata", category="alert alert-warning")
            return redirect(url_for('log'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    flash("Logout effettuato con successo", category='alert alert-success')
    return redirect(url_for('log'))

@app.route('/homepage/utente/<username>', methods=['GET', 'POST'])
@login_required
def utente(username):
    user = Users.query.filter_by(username=username).first()
    return render_template('home_utente.html', user=user)

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
                password=password,
                email=email,
                sesso=sesso,
                eta=eta,
                ruolo=ruolo
            )
            db.session.add(user)
            db.session.commit()
            flash("Registrazione riuscita", category="alert alert-success")
            # Dopo la registrazione, reindirizza alla pagina degli interessi
            return redirect(url_for('interessi'))
        except IntegrityError:
            db.session.rollback()
            flash("ERROR: Utente già registrato", category="alert alert-warning")
            return render_template('registrazione.html')

    return render_template('registrazione.html')

@app.route('/registrazione/interessi', methods=['GET', 'POST'])
def interessi():
    if request.method == "GET":
        return render_template('interessi.html')
    else:  # if POST
        details = request.form
        interessi = details.getlist('interessi')
        errore = False

        try:
            username = current_user 
            for interesse in interessi:
                db.engine.execute("INSERT INTO user_interessi (username, id_interessi) VALUES (%s, %s)", (username, interesse))
            flash("Interessi aggiunti correttamente", category="alert alert-success")
        except IntegrityError:
            flash("Errore nell'aggiunta degli interessi", category="alert alert-warning")
            return render_template('interessi.html')

        # Dopo aver aggiunto gli interessi, reindirizza alla pagina di login
        return redirect(url_for('login.log'))

@app.route('/<string:username>/modifica_profilo', methods=['GET', 'POST'])
@login_required
def modifica_profilo():
    if request.method == 'POST':
        details = request.form
        new_username = details.get('username')
        new_nome = details.get('nome', current_user.nome)
        new_cognome = details.get('cognome', current_user.cognome)
        new_sesso = details.get('sesso', current_user.sesso)
        new_eta = details.get('eta', current_user.eta)

        # Verifica se lo username è già stato usato da un altro utente
        if new_username != current_user.username and Users.query.filter_by(username=new_username).first():
            flash('Lo username scelto è già in uso, scegline un altro', 'alert alert-warning')
            return redirect(url_for('app.modifica_profilo'))

        try:
            current_user.username = new_username
            current_user.nome = new_nome
            current_user.cognome = new_cognome
            current_user.sesso = new_sesso
            current_user.eta = new_eta

            db.session.commit()
            flash('Informazioni del profilo aggiornate con successo', 'alert alert-success')
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'aggiornamento del profilo: {str(e)}', 'alert alert-danger')

        return redirect(url_for('app.modifica_profilo'))

    return render_template('modifica_profilo.html', user=current_user)

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

@app.route('/commenti/<string:utente>', methods=['POST'])
@login_required
def commenta_post(post_id):
    details = request.form
    contenuto = details.get('contenuto')

    if not contenuto:
        flash('Il commento non può essere vuoto', 'alert alert-warning')
            
    if current_user.is_inserzionista:
        return render_template('inserzionista_home')
    else:
        return render_template('utente_home')
        return redirect(url_for('utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

    nuovo_commento = Comment(contenuto=contenuto, autore=current_user.username, post_id=post_id, data_commento=datetime.now())

    try:
        db.session.add(nuovo_commento)
        db.session.commit()
        flash('Commento aggiunto con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'aggiunta del commento: {str(e)}', 'alert alert-danger')
        
    if current_user.is_inserzionista:
        return render_template('inserzionista_home')
    else:
        return render_template('utente_home')
    

@app.route('/elimina_commento/<int:comment_id>', methods=['DELETE'])
@login_required
def elimina_commento(id):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se il commento esiste e appartiene all'utente corrente
        cursor.execute("SELECT * FROM post_comments WHERE id = ? AND utentec = ?", (id, current_user))
        commento = cursor.fetchone()
        
        if commento is None:
            return jsonify({"message": "Commento non trovato o non autorizzato"}), 404
        
        # Elimina il commento
        cursor.execute("DELETE FROM post_comments WHERE id = ?", (id))
        
        conn.commit()
        return jsonify({"message": "Commento eliminato con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('commenti.html', user=utente)

#------------------------------ inserimento mi piace -------------------------------#

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

#------------------------------ seguire e accettare -------------------------------#

    # inviare una richiesta ad una persona

@app.route('/richieste/<string:utente>', methods=['POST'])
@login_required
def invia_richiesta(utente):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Inserisci una nuova richiesta di amicizia
        cursor.execute("""
            INSERT INTO amici (io_utente, user_amico, stato_richiesta)
            VALUES (?, ?, ?)
        """, (current_user, utente, 'in_attesa'))
        
        conn.commit()
        return jsonify({"message": "Richiesta di amicizia inviata con successo"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"message": "Errore: richiesta di amicizia già inviata o utente non esistente"}), 400

    finally:
        conn.close()
        return render_template('profilo_amico.html', user=utente)

    # accettare una richiesta

@app.route('/richieste/<string:utente>', methods=['POST'])
@login_required
def accetta_richiesta(utente):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Aggiorna lo stato della richiesta di amicizia
        cursor.execute("""
            UPDATE amici
            SET stato_richiesta = ?
            WHERE io_utente = ? AND user_amico = ? AND stato_richiesta = ?
        """, ('accettata', utente, current_user, 'in_attesa'))
        
        if cursor.rowcount == 0:
            return jsonify({"message": "Errore: richiesta di amicizia non trovata o già accettata"}), 400
        
        conn.commit()
        return jsonify({"message": "Richiesta di amicizia accettata con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('profilo_amico.html', user=utente)

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

@app.route('/cerca_utente', methods=['GET', 'POST'])
@login_required
def cerca_utente():
    if request.method == 'POST':
        search_term = request.form.get('search_term', '')
        risultati_ricerca = Users.query.filter(Users.username.ilike(f'%{search_term}%')).all()
        return render_template('risultati_ricerca.html', risultati=risultati_ricerca, search_term=search_term)
    
    return render_template('cerca_utente.html')

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
