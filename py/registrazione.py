from flask import Blueprint, render_template, flash, url_for, redirect, request
from .create import db
from .function import check_password, check_email, encode_pwd
from sqlalchemy.exc import IntegrityError

registrazione = Blueprint('registrazione', __name__)

#------------------------------ registrazione utente -------------------------------#

@registrazione.route('/registrazione', methods=['GET', 'POST'])
def addprofile():
    if request.method == "GET":
        return render_template('registrazione.html')
    else:  # if POST
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

        # Validazione dei campi e gestione degli errori

        if errore:
            return render_template('registrazione.html')

        pw_crypt = encode_pwd(password)
        try:
            db.engine.execute(
                    "INSERT INTO users (username, nome, cognome, password, email, sesso, eta, ruolo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                    (username, nome, cognome, pw_crypt, email, sesso, eta, ruolo)
                )
            flash("Registrazione riuscita", category="alert alert-success")
            # Dopo la registrazione, reindirizza alla pagina degli interessi
            return redirect(url_for('register.interessi'))
        except IntegrityError:
            flash("ERROR: Utente già registrato", category="alert alert-warning")
            return render_template('registrazione.html')

	
#------------------------------ interessi utente -------------------------------#

@registrazione.route('/registrazione/interessi', methods=['GET', 'POST'])
def interessi():
    if request.method == "GET":
        return render_template('interessi.html')
    else:  # if POST
        details = request.form
        interessi = details.getlist('interessi')
        errore = False

        try:
            username = get_current_user_id() 
            for interesse in interessi:
                db.engine.execute("INSERT INTO user_interessi (username, id_interessi) VALUES (%s, %s)", (username, interesse))
            flash("Interessi aggiunti correttamente", category="alert alert-success")
        except IntegrityError:
            flash("Errore nell'aggiunta degli interessi", category="alert alert-warning")
            return render_template('interessi.html')

        # Dopo aver aggiunto gli interessi, reindirizza alla pagina di login
        return redirect(url_for('login.log'))
