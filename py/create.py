from sqlalchemy import Column, Integer, String, Text, BLOB, ForeignKey, TIMESTAMP, Date, func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime  # Importa datetime solo una volta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Ruolo(enum.Enum):
    utente = "utente"
    pubblicitari = "pubblicitari"
    
class Tipo_Post(enum.Enum):
    immagini = "immagini"
    video = "video"
    testo = "testo"

class Stato(enum.Enum):
    accettato = "accettato"
    in_attesa = "in attesa"
    non_accettato= "non accettato"

class Sesso(enum.Enum):
    maschio = "maschio"
    femmina = "femmina"
    altro = "altro"


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    immagine = Column(BLOB, nullable=True)
    nome = Column(String(50), unique=False, nullable=False)
    cognome = Column(String(50), unique=False, nullable=False)
    password = Column(String(150), nullable=False)  # Renamed to password_hash
    email = Column(String(150), unique=True, nullable=False)
    sesso = Column(db.Enum(Sesso))
    eta = Column(Integer, unique=False, nullable=False)
    ruolo = Column(db.Enum(Ruolo))

    def __init__(self, username, nome, cognome, password, email, sesso, eta, ruolo, immagine=None):
        self.username = username
        self.immagine = immagine
        self.nome = nome
        self.cognome = cognome
        self.password = password
        self.email = email
        self.sesso = sesso
        self.eta = eta
        self.ruolo = ruolo

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True
    
    #@property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    #@password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def url_photo(self):
        if self.profile_picture:
            return '/contenuti/'+self.profile_picture
        else:
            return None

class Interessi(db.Model, UserMixin):
    __tablename__ = 'interessi'
    
    id_interessi = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), unique=False, nullable=False) 

    def __init__(self, id_interessi , nome):
        self.id_interessi= id_interessi
        self.nome = nome

class UserInteressi(db.Model, UserMixin):  # Renamed to UserInteressi
    __tablename__ = 'user_interessi'
    
    utente = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    id_interessi = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False, primary_key=True)
    
    users = db.relationship('Users', backref= db.backref('interessi', cascade='all, delete-orphan'))
    interessi = db.relationship('Interessi', backref= db.backref('interessi', cascade='all, delete-orphan'))

    def __init__(self, utente, id_interessi):
        self.utente = utente
        self.id_interessi = id_interessi

class Amici(db.Model, UserMixin):
    __tablename__ = 'amici'
    
    io_utente = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    user_amico = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    stato = Column(db.Enum(Stato))

    users = db.relationship('Users', backref= db.backref('users', cascade='all, delete-orphan'))
    

    def __init__(self, io_utente, user_amico, stato):
        self.io_utente = io_utente
        self.user_amico = user_amico
        self.stato = stato
  

class Post(db.Model, UserMixin):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    utente = Column(String(50), ForeignKey('users.username'), nullable=False)
    media = Column(BLOB, nullable=True)
    tipo_post = Column(db.Enum(Tipo_Post))
    data_creazione = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    testo = Column(Text, nullable=True)
    
    users = db.relationship('Users', backref= db.backref('Post', cascade='all, delete-orphan'))


    #user = relationship("Users", back_populates="posts")
    
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
    
    posts = db.relationship('posts', backref= db.backref('Postcomments', cascade='all, delete-orphan'))
    users = db.relationship('users', backref= db.backref('Postcomments', cascade='all, delete-orphan'))


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
    
    posts = db.relationship('posts', backref= db.backref('Postlikes', cascade='all, delete-orphan'))
    users = db.relationship('users', backref= db.backref('Postlikes', cascade='all, delete-orphan'))

    def __init__(self, post_id, username, content=None):
        self.post_id = post_id
        self.username = username
        self.content = content

class Annunci(db.Model, UserMixin):
    __tablename__ = 'annunci'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    advertiser = Column(String(50), ForeignKey('users.username'), nullable=False)
    tipo_post = Column(db.Enum(Tipo_Post))
    sesso_target = Column(db.Enum(Sesso))
    eta_target = Column(Integer, unique=False, nullable=False)
    interesse_target = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False)
    inizio = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    fine = Column(Date, default=datetime.utcnow)  # Usa datetime.utcnow senza le parentesi
    
    users = db.relationship('users', backref= db.backref('annunci', cascade='all, delete-orphan'))
    interessi = db.relationship('Interessi', backref= db.backref('annunci', cascade='all, delete-orphan'))


    def __init__(self, advertiser, tipo_post, sesso_target, eta_target, interesse_target, fine):
        self.advertiser = advertiser
        self.tipo_post = tipo_post
        self.sesso_target = sesso_target
        self.eta_target = eta_target
        self.interesse_target = interesse_target
        self.fine = fine

    def url_photo(self):
        return '/contenuti/' + self.cover_picture


class AnnunciLikes(db.Model, UserMixin):
    __tablename__ = 'annunci_likes'
    
    annuncio_id = Column(Integer, ForeignKey('annunci.id'), primary_key=True, nullable=False)
    username = Column(String(50), ForeignKey('users.username'), primary_key=True, nullable=False)
    clicked_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    
    users = db.relationship('users', backref= db.backref('annuncilikes', cascade='all, delete-orphan'))
    annuncio = db.relationship('annunci', backref= db.backref('annuncilikes', cascade='all, delete-orphan'))

    def __init__(self, annuncio_id, username):
        self.annuncio_id = annuncio_id
        self.username = username
    
class AnnunciComments(db.Model, UserMixin):
    __tablename__ = 'annunci_comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    annuncio_id = Column(Integer, ForeignKey('annunci.id'), nullable=False)
    utentec = Column(String(50), ForeignKey('users.username'), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    
    users = db.relationship('users', backref= db.backref('annuncicomments', cascade='all, delete-orphan'))
    annuncio = db.relationship('annunci', backref= db.backref('annuncicomments', cascade='all, delete-orphan'))

    def __init__(self, annuncio_id, utentec, content=None):
        self.annuncio_id = annuncio_id
        self.utentec = utentec
        self.content = content

class Target(db.Model, UserMixin):
    __tablename__ = "target"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sesso = Column(db.Enum(Sesso))
    eta = Column(Integer, unique=False, nullable=False)
    interesse = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False)
    
    interessi = db.relationship('interessi', backref= db.backref('target', cascade='all, delete-orphan'))

    def __init__(self, sesso, eta, interesse):
        self.sesso = sesso
        self.eta = eta
        self.interesse = interesse
