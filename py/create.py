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

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    immagine = Column(BLOB, nullable=True)
    nome = Column(String(50), unique=False, nullable=False)
    cognome = Column(String(50), unique=False, nullable=False)
    password_hash = Column(String(150), nullable=False)  # Renamed to password_hash
    email = Column(String(150), unique=True, nullable=False)
    sesso = Column(db.Enum(Sesso))
    eta = Column(Integer, unique=False, nullable=False)
    ruolo = Column(db.Enum(Ruolo))

    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)
    
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
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
    
class UserInteressi(db.Model, UserMixin):  # Renamed to UserInteressi
    __tablename__ = 'user_interessi'
    
    utente = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    id_interessi = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False, primary_key=True)
    
class Amici(db.Model, UserMixin):  # Renamed to Amici
    __tablename__ = 'amici'
    
    io_utente = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    user_amico = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    stato = Column(db.Enum(Stato))  

class Post(db.Model, UserMixin):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    utente = Column(String(50), ForeignKey('users.username'), nullable=False)
    media = Column(BLOB, nullable=True)
    tipo_post = Column(db.Enum(Tipo_Post))
    data_creazione = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    testo = Column(Text, nullable=True)
    
    # Definire la relazione se necessario
    user = relationship("Users", back_populates="posts")
    
    def url_photo(self):
        return '/contenuti/'+self.cover_picture

class PostComments(db.Model, UserMixin):  # Renamed to PostComments
    __tablename__ = 'post_comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'), autoincrement=True)
    utentec = Column(String(50), ForeignKey('users.username'), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    
class PostLikes(db.Model, UserMixin):  # Renamed to PostLikes
    __tablename__ = 'post_likes'
    
    post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey('users.username'), primary_key=True, nullable=False)
    content = Column(Text, nullable=True)
    clicked_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

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

    def url_photo(self):
        return '/contenuti/'+self.cover_picture

class AnnunciLikes(db.Model, UserMixin):  # Renamed to AnnunciLikes
    __tablename__ = 'annunci_likes'
    
    annuncio_id = Column(Integer, ForeignKey('annunci.id'), primary_key=True, nullable=False)
    username = Column(String(50), ForeignKey('users.username'), primary_key=True, nullable=False)
    clicked_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    
class AnnunciComments(db.Model, UserMixin):  # Renamed to AnnunciComments
    __tablename__ = 'annunci_comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    annuncio_id = Column(Integer, ForeignKey('annunci.id'), nullable=False)
    utentec = Column(String(50), ForeignKey('users.username'), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

class Target(db.Model, UserMixin):  # Renamed to Target
    __tablename__ = "target"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sesso = Column(db.Enum(Sesso))
    eta = Column(Integer, unique=False, nullable=False)
    interesse = Column(Integer, ForeignKey('interessi.id_interessi'), nullable=False)
