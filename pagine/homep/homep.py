from flask import Blueprint, render_template
from flask_login import login_required

home_inserzionista_bp = Blueprint('home_inserzionista', __name__)

@home_inserzionista_bp.route('/')
@login_required
def home():
    return render_template('home_inserzionista.html')
