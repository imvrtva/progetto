# funzioni:
# get_current_user_id(), login_user(user)
from flask import Flask, request, url_for, redirect, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from datetime import datetime
from .create import *

#---------------------------- password --------------------------#

    ## codifica

def encode_pwd(pwd):
    pw_hash = bcrypt.generate_password_hash(pwd, 10).decode("utf-8")
    return pw_hash

    ## decodifica

def decode_pwd(hash_pwd,real_pwd):
    return bcrypt.check_password_hash(hash_pwd, real_pwd)

    ## controllo password

def check_password(password):
	length_errore = len(password) < 8
	digit_errore = re.search(r"\d", password) is None
	uppercase_errore = re.search(r"[A-Z]", password) is None
	lowercase_errore = re.search(r"[a-z]", password) is None

	errore = not(length_errore or digit_errore or uppercase_errore or lowercase_errore)

	return errore

#---------------------------- email ----------------------------#

def check_email(email):
	regexEmail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Z|a-z]{2,}\b'
	errore = (re.fullmatch(regexEmail, email))

	return errore
