#creare classi dinamiche e non
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import Enum
import enum
import datetime

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()



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
    

        
class users(db.Model, UserMixin):
    tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username= Column(String(50), unique=True, nullable=False, primary_key=True)
    immagine = Column(BLOB, nullable=True)
    nome = Column(String(50), unique=False, nullable=False)
    cognome = Column(String(50), unique=False, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    sesso = db.Column(db.Enum(Sesso))
    eta = Column(Integer, unique=False, nullable=False)
    ruolo = db.Column(db.Enum(Ruolo))


    def __init__(self, **kwargs):
        super(Utente, self).__init__(**kwargs)
    
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


class Interessi (db.Model, UserMixin):
    tablename__ = 'interessi'
    
    id_interessi = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), unique=False, nullable=False)        
    
class User_interessi (db.Model, UserMixin):   
    tablename__ = 'user_interessi'
    
    utente = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    id_interessi = Column(String(50), ForeignKey('interessi.id_interessi'), nullable=False, primary_key=True)
    
class Amici (db.Model, UserMixin):   
    tablename__ = 'amici'
    
    io_utente = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    user_amico = Column(String(50), ForeignKey('users.username'), nullable=False, primary_key=True)
    stato = db.Column(db.Enum(Stato))  

class Post(db.Model, UserMixin):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    utente = Column(String(50), ForeignKey('users.username'), nullable=False)
    media = Column(BLOB, nullable=True)
    tipo_post = db.Column(db.Enum(Tipo_Post))
    data_creazione = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    testo = Column(Text, nullable=True)
    
    # Definire la relazione se necessrio
    user = relationship("User", back_populates="posts")
    
    def url_photo(self):
        return '/contenuti/'+self.cover_picture

class Post_comments(db.Model, UserMixin):
    __tablename__ = 'post_comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, pForeignKey('posts.id'), autoincrement=True)
    utentec = Column(String(50), ForeignKey('users.username'), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    
class Post_likes(db.Model, UserMixin):
    __tablename__ = 'post_likes'
    
    post_id = Column(Integer, pForeignKey('posts.id'),primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey('users.username'),primary_key=True, nullable=False)
    content = Column(Text, nullable=True)
    cliked_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

class Annunci(db.Model, UserMixin):
    __tablename__ = 'annunci'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    advertiser = Column(String(50), ForeignKey('users.username'), nullable=False)
    tipo_post = db.Column(db.Enum(Tipo_Post))
    sesso_target = db.Column(db.Enum(Sesso))
    eta_target = Column(Integer, unique=False, nullable=False)
    interesse_target = Column(String(50), ForeignKey('interessi.id_interessi'), nullable=False)
    inizio = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    fine = Column(Date, default=datetime.utcnow)
    
def url_photo(self):
        return '/contenuti/'+self.cover_picture
    
    
class Annunci_likes(db.Model, UserMixin):
    __tablename__ = 'annunci_likes'
    
    annuncio_id = Column(String(50), ForeignKey('annunci.id'), primary_key=True, nullable=False)
    username= Column(String(50), ForeignKey('users.username'), primary_key=True, nullable=False)
    clicked_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    
class Annunci_comments(db.Model, UserMixin):
    __tablename__ = 'annunci_comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    annuncio_id = Column(String(50), ForeignKey('annunci.id'), nullable=False)
    utentec= Column(String(50), ForeignKey('users.username'), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

class Target (db.Model, UserMixin):
    __tablename__="target"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sesso = db.Column(db.Enum(Sesso))
    eta = Column(Integer, unique=False, nullable=False)
    interesse = Column(String(50), ForeignKey('interessi.id_interessi'), nullable=False)
    

