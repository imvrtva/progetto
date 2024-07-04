from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

pubblicare_bp = Blueprint('pubblicare', __name__)

@pubblicare_bp.route('/', methods=['GET', 'POST'])
@login_required
def publish():
    if request.method == 'POST':
        content = request.form.get('content')
        # Logica per salvare il post o l'inserzione
        return redirect(url_for('home_utente.home'))
    return render_template('pubblicare.html')
