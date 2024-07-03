from flask import Blueprint, render_template
from flask_login import login_required, current_user

profili_bp = Blueprint('profili', __name__)

@profili_bp.route('/<user_id>')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    return render_template('profili.html', user=user)
