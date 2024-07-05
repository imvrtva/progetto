from flask import Blueprint, render_template, flash, url_for, redirect, request
from .create import db
from .function import check_password, check_email
from sqlalchemy.exc import IntegrityError

register = Blueprint('register', __name__)

#------------------------------ registrazione utente -------------------------------#

@register.route('/registrazione', methods=['GET', 'POST'])
def addprofile():
	if request.method == "GET":
		return render_template('template/registrazione.html')
	else: #if post
		details = request.form
		print(details)
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

		if (not check_email(email)):
			flash("Formato email sbagliato", "alert alert-warning")
			errore = True
		if cpassword != password:
			flash("Le Passoword sono diverse", "alert alert-warning")
			errore = True
		if not check_password(password):
			flash("Formato password sbagliato", "alert alert-warning")
			errore = True
		if errore:
			return render_template('registrazione.html')
		pw_crypt = encode_pwd(password)
		try:
			db.engine.execute(
					"INSERT INTO users VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", 
					( username , nome , cognome , pw_crypt , email ,sesso , eta , ruolo )
				)
			flash("Registrazione riuscita", category="alert alert-success")
		except:
			flash("ERROR: Utente gia registrato ", "alert alert-warning")
			return render_template('registrazione.html')
		return redirect(url_for('registrazione.interessi'))
	
#------------------------------ interessi utente -------------------------------#

@register.route('/registrazione/interessi', methods=['GET', 'POST'])
def interessi():
	if request.method == "GET":
		return render_template('interessi.html')
	else: #if post
		details = request.form
		interessi = details['interessi']
		interessi = ','.join(details.getlist('interessi'))
		errore = False

	try:
		username = get_current_user_id() 
		db.engine.execute("INSERT INTO user_interessi VALUES(%s,%s)", (username , interessi))
		flash("Interessi aggiunti correttamente", category="alert alert-success")
	except IntegrityError:
		flash("Errore nell'aggiunta degli interessi", "alert alert-warning")
		return render_template('interessi.html')
	return redirect(url_for('login.log'))