# app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from py.create import *  # Assicurati che le funzioni siano importate correttamente
from py.login import login  
from .registrazione import registrazione  # Assicurati che 'addprofile' sia importato correttamente

name = "postgres"
password = "ciao"
namedb = "progetto"

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    create_database()
    app.config['SECRET_KEY'] = 'stringasegreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ciao@localhost/progettobasi'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    db.init_app(app)
    create_tabledb(app)
    
    # Registra i Blueprint con l'applicazione
    #app.register_blueprint(log, url_prefix='/')
    #app.register_blueprint(addprofile, url_prefix='/registrazione')
    
    # Configura il login manager
    app.register_blueprint(login, url_prefix='/login')
    app.register_blueprint(registrazione, url_prefix='/register')
	#login
    login_manager.login_view = 'login.log'
    login_manager.init_app(app)
    bcrypt.init_app(app)
    return app

# Parte per inizializzare il database
# Crea tabelle da file SQL e inserisce valori di base
def create_tabledb(app):
    file_text = open("./database/database.sql").read()
    file_insetion = open("./database/insert.sql").read()
    
    try:
        with app.app_context():
            db.engine.execute(text(file_text))
            db.engine.execute(text(file_insetion))
    except Exception as e:
        print('Tabelle già presenti') 

def create_database():
    try: 
        con = psycopg2.connect(dbname='progettobasi', user=name, host='localhost',
                               password='ciao' , port="5433")
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) 
        cursor = con.cursor() 
        exe = "create database "+namedb+";"
        cursor.execute(exe)
    except: 
        print("\nDatabase già presente\n")
