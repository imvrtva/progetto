from flask import Blueprint, render_template, flash, url_for, redirect, request
from .create import db
from .auth import *
from .function import check_password, check_email
import re

ruolo_standard = 'utente'
register = Blueprint('register', __name__)



@register.route('/', methods=['GET', 'POST'])
def addprofile():
	if request.method == "GET":
		return render_template('profileReg.html')
	else: #if post
		details = request.form
		print(details)
		codfisc = details['codfiscale']
		firstName = details['fname']
		lastName = details['lname']
		age = details['age']
		sex = details['sex']
		phonenumber = details['phone']
		email = details['email']
		password = details['password']
		cpassword = details['cpassword']

		errore = False

		if (not check_email(email)):
			flash("Formato email sbagliato", "alert alert-warning")
			errore = True
		if not cpassword == password:
			flash("Le Passoword sono diverse", "alert alert-warning")
			errore = True
		if not check_password(password):
			flash("Formato password sbagliato", "alert alert-warning")
			errore = True
		if errore:
			return render_template('profileReg.html')
		pw_crypt = encode_pwd(password)
		try:
			db.engine.execute("INSERT INTO Utenti VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (codfisc, firstName,lastName ,age ,sex ,phonenumber,email,pw_crypt, ruolo_standard))
			flash("Registrazione riuscita", category="alert alert-success")
		except:
			flash("ERROR: Utente gia reggistrato ", "alert alert-warning")
			return render_template('profileReg.html')
		return redirect(url_for('login.log'))