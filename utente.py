from flask import request, url_for, redirect, render_template, jsonify, Blueprint, flash
from flask_login import login_required, current_user
from .create import *
from .function import *
from .models import User, Post, Comment, Like, Follow
from datetime import datetime

ruolo_standard = 'utente'
utente = Blueprint('utente', __name__)

#------------------------------ modifica info profilo -------------------------------#

@utente.route('/<string:username>/modifica_profilo', methods=['GET', 'POST'])
@login_required
def modifica_profilo():
    if request.method == 'POST':
        details = request.form
        new_username = details.get('username')
        new_nome = details.get('nome', current_user.nome)
        new_cognome = details.get('cognome', current_user.cognome)
        new_sesso = details.get('sesso', current_user.sesso)
        new_eta = details.get('eta', current_user.eta)

        # Verifica se lo username è già stato usato da un altro utente
        if new_username != current_user.username and User.query.filter_by(username=new_username).first():
            flash('Lo username scelto è già in uso, scegline un altro', 'alert alert-warning')
            return redirect(url_for('utente.modifica_profilo'))

        try:
            current_user.username = new_username
            current_user.nome = new_nome
            current_user.cognome = new_cognome
            current_user.sesso = new_sesso
            current_user.eta = new_eta

            db.session.commit()
            flash('Informazioni del profilo aggiornate con successo', 'alert alert-success')
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'aggiornamento del profilo: {str(e)}', 'alert alert-danger')

        return redirect(url_for('utente.modifica_profilo'))

    return render_template('modifica_profilo.html', user=current_user)

#------------------------------ pubblicazione post -------------------------------#

    ## pubblicazione testo
    ## pubblicazione immagine
    ## pubblicazione video

@utente.route('/<string:username>/pubblicazione', methods=['POST'])
@login_required
def pubblica(username):
    contenuto = request.form.get('contenuto')
    file = request.files['photo-profile']
    filename = secure_filename(file.filename)
    media = request.files('media')  # Assume che il file multimediale venga inviato tramite POST
    tipo_post = request.form.get('tipo_post')  # Assume che ci sia un campo 'tipo_post' nel form

    if not contenuto and not media:
        flash('Il post non può essere vuoto', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))

    # Gestione dell'upload del file multimediale (se presente)
    media_blob = None
    if media:
        media_blob = media.read()  # Leggi i dati del file multimediale in un blob di byte

    nuovo_post = Post(
        utente=current_user.username,
        media=media_blob,
        tipo_post=tipo_post,
        data_creazione=datetime.now(),
        testo=contenuto
    )

    try:
        db.session.add(nuovo_post)
        db.session.commit()
        flash('Post pubblicato con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante la pubblicazione del post: {str(e)}', 'alert alert-danger')

    return redirect(url_for('utente.pubblica(username)'))

@utente.route('/pubblica/testo/<username>', methods=['POST'])
@login_required
def post_testo(username):
    contenuto = request.form.get('contenuto')
    tipo_post = request.form.get('tipo_post')  # Assume che ci sia un campo 'tipo_post' nel form

    if not contenuto:
        flash('Il post non può essere vuoto', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))

    nuovo_post = Post(
        utente=current_user.username,
        tipo_post=tipo_post,
        data_creazione=datetime.now(),
        testo=contenuto
    )

    try:
        db.session.add(nuovo_post)
        db.session.commit()
        flash('Post pubblicato con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante la pubblicazione del post: {str(e)}', 'alert alert-danger')

    return redirect(url_for('utente.pubblica', username=username))

@utente.route('/pubblica/video/<username>', methods=['POST'])
@login_required

def post_video(username):
    file = request.files.get('video')
    contenuto = request.form.get('contenuto')

    if not file or file.filename == '':
        flash('Nessun file selezionato', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))

    filename = secure_filename(file.filename)
    file.save(os.path.join('path/to/save', filename))  # Specifica il percorso dove salvare il file

    nuovo_post = Post(
        utente=current_user.username,
        tipo_post='video',
        data_creazione=datetime.now(),
        testo=contenuto,
        media=filename
    )

    try:
        db.session.add(nuovo_post)
        db.session.commit()
        flash('Post di video pubblicato con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante la pubblicazione del post: {str(e)}', 'alert alert-danger')

    return redirect(url_for('utente.pubblica', username=username))

@utente.route('/pubblica/immagine/<username>', methods=['POST'])
@login_required

def post_immagine(username):
    file = request.files.get('photo')
    contenuto = request.form.get('contenuto')

    if not file or file.filename == '':
        flash('Nessun file selezionato', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))

    filename = secure_filename(file.filename)
    file.save(os.path.join('path/to/save', filename))  # Specifica il percorso dove salvare il file

    nuovo_post = Post(
        utente=current_user.username,
        tipo_post='immagine',
        data_creazione=datetime.now(),
        testo=contenuto,
        media=filename
    )

    try:
        db.session.add(nuovo_post)
        db.session.commit()
        flash('Post di immagine pubblicato con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante la pubblicazione del post: {str(e)}', 'alert alert-danger')

    return redirect(url_for('utente.pubblica', username=username))



#------------------------------ inserimento commenti -------------------------------#

@utente.route('/commenti/<string:utente>', methods=['POST'])
@login_required
def commenta_post(post_id):
    details = request.form
    contenuto = details.get('contenuto')

    if not contenuto:
        flash('Il commento non può essere vuoto', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

    nuovo_commento = Comment(contenuto=contenuto, autore=current_user.username, post_id=post_id, data_commento=datetime.now())

    try:
        db.session.add(nuovo_commento)
        db.session.commit()
        flash('Commento aggiunto con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'aggiunta del commento: {str(e)}', 'alert alert-danger')
    
    return redirect(url_for('login.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

#------------------------------ inserimento mi piace -------------------------------#

@utente.route('/mi_piace/<int:post_id>', methods=['POST'])
@login_required
def mi_piace(post_id):
    post = Post.query.get(post_id)

    if not post:
        flash('Il post non esiste', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

    if current_user.username == post.autore:
        flash('Non puoi mettere mi piace al tuo stesso post', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

    nuovo_like = Like(post_id=post_id, username=current_user.username)

    try:
        db.session.add(nuovo_like)
        db.session.commit()
        flash('Mi piace aggiunto con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'aggiunta del mi piace: {str(e)}', 'alert alert-danger')
    
    return redirect(url_for('login.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

#------------------------------ seguire una persona -------------------------------#

@utente.route('/segui_utente/<string:username_da_seguire>', methods=['POST'])
@login_required
def segui_utente(username_da_seguire):
    if username_da_seguire == current_user.username:
        flash('Non puoi seguire te stesso', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

    utente_da_seguire = User.query.filter_by(username=username_da_seguire).first()

    if not utente_da_seguire:
        flash('L\'utente da seguire non esiste', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

    if current_user.is_following(utente_da_seguire):
        flash('Hai già iniziato a seguire questo utente', 'alert alert-warning')
        return redirect(url_for('login.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

    try:
        current_user.follow(utente_da_seguire)
        db.session.commit()
        flash(f'Adesso stai seguendo {username_da_seguire}', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante il seguimento dell\'utente: {str(e)}', 'alert alert-danger')
    
    return redirect(url_for('login.utente_home'))  # Modifica il nome della funzione a seconda della tua implementazione

#------------------------------ ricerca utente -------------------------------#

@utente.route('/cerca_utente', methods=['GET', 'POST'])
@login_required
def cerca_utente():
    if request.method == 'POST':
        search_term = request.form.get('search_term', '')
        risultati_ricerca = User.query.filter(User.username.ilike(f'%{search_term}%')).all()
        return render_template('risultati_ricerca.html', risultati=risultati_ricerca, search_term=search_term)
    
    return render_template('cerca_utente.html')
