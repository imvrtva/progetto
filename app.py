from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
name = "postgres"
password = "ciao"
namedb = "daisunive8"

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
	app = Flask(__name__)
	create_database()
	app.config['SECRET_KEY'] = 'stringasegreta'
	app.config['SQLALCHEMY_DATABASE_URI']  = 'postgresql://'+name+':'+password+'@localhost:5432/'+namedb
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	print("\n richiama create_app\n")

	db.init_app(app)

	create_tabledb(app)
	
	from .login import log
	from .registrazione import addprofile
	app.register_blueprint(login, url_prefix='/login')
	app.register_blueprint(register, url_prefix='/registrazione')
	#login
	login_manager.login_view = 'login.log'
	login_manager.init_app(app)
	bcrypt.init_app(app)
	

	return app

#parte per inizializzare db
#crea tabelle da file sql 
def create_tabledb(app):
    file_text = open("./database/database.sql").read()
    file_insetion = open("./database/insert.sql").read()
    #creazione tabelle database se non presenti e inserzione valori di basi
    try:
        with app.app_context():
            db.engine.execute(text(file_text))
            db.engine.execute(text(file_insetion))
    except Exception as e:
        print('gia prensenti tebales') 


def create_database():
	try: 
		con = psycopg2.connect(dbname='postgres',user=name, host='localhost',
			password=password , port="5432")
		con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) 
		cursor = con.cursor() 
		exe = "create database "+namedb+";"
		cursor.execute(exe)
	except: 
		print("\ndatabase gia presente\n")

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
