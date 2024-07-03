from flask import Blueprint, render_template
from flask_login import login_required

home_utente_bp = Blueprint('home_utente', __name__)

@home_utente_bp.route('/')
@login_required
def home():
    return render_template('home_utente.html')
