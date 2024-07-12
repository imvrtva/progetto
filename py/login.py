#route login
# scelta interessi
from flask import request, url_for, redirect, render_template, jsonify, Blueprint, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_bcrypt import bcrypt
from py.create import *
from py.function import *


login = Blueprint('login', __name__)

#------------------------------ accesso utente -------------------------------#

@login.route('/login', methods=['GET', 'POST'])
def log():
    if request.method == "POST":
        details = request.form
        email = details['email']
        pw = details['password']

        result = db.engine.execute("SELECT * FROM users WHERE email = %s", (email,))
        queryUser = result.fetchone()

        if queryUser:
            if bcrypt.check_password_hash(queryUser.password, pw):
                user = utente(queryUser.username, queryUser.nome, queryUser.cognome, 
                              queryUser.password, queryUser.email, queryUser.sesso, 
                              queryUser.eta, queryUser.ruolo)
                login_user(user)
                if user.ruolo == 'utente':
                    return redirect(url_for('utente', username=user.username))
                elif user.ruolo == 'inserzionista':
                    return redirect(url_for('inserzionista', username=user.username))
            else:
                flash("Password sbagliata", category="alert alert-warning")
                return redirect(url_for('log'))  
        else:
            flash("Questa email non è registrata", category="alert alert-warning")
            return redirect(url_for('log'))  
    else:
        return render_template('login.html')


#------------------------------ logout utente -------------------------------#

@login.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout effettuato", category='alert alert-success')
    return redirect(url_for('login.log'))

#--------------------------- ruolo utente normale ---------------------------#

    ## homepage utente

@login.route('/utente/<string:username>', methods=['GET', 'POST'])
@login_required
def utente():
    if current_user.ruolo == 'utente':
        return render_template("home_utente.html")
    else:
        flash("Accesso non autorizzato", category="alert alert-warning")
        return redirect(url_for('login.log'))

     
#--------------------------- ruolo utente inserzionista ---------------------------#

    ## homepage inserzionista

@login.route('/inserzionista/<string:username>', methods=['GET', 'POST'])
@login_required
def inserzionista():
    if current_user.ruolo == 'inserzionista':
        return render_template("template/home_inserzionista.html")
    else:
        flash("Accesso non autorizzato", category="alert alert-warning")
        return redirect(url_for('login.log'))
     
