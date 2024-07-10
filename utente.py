from flask import request, url_for, redirect, render_template, jsonify, Blueprint, flash
from flask_login import login_required, current_user
from .create import *
from .function import *
from .create import User, posts, Comment, Like, Follow
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import sqlite3

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
 
@utente.route('/pubblica/testo/<username>', methods=['POST'])
@login_required
def post_testo(username):
    contenuto = request.form.get('contenuto')
    tipo_post = request.form.get('tipo_post','testo')  # Assume che ci sia un campo 'tipo_post' nel form

    if not contenuto:
        flash('Il post non può essere vuoto', 'alert alert-warning')
        return render_template('template/pubblicazione_testo.html') # rimane nella stessa pagina html

    nuovo_post = posts(
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
        flash('Errore durante la pubblicazione del post: {str(e)}', 'alert alert-danger')

    return render_template('template/home_utente.html')

    ## pubblicazione video

@utente.route('/pubblica/video/<username>', methods=['POST'])
@login_required
def post_video(username):
    file = request.files.get('video')
    contenuto = request.form.get('contenuto')

    if not file or file.filename == '':
        flash('Nessun file selezionato', 'alert alert-warning')
        return render_template('template/pubblicazione_video.html')

    filename = secure_filename(file.filename)
    file.save(os.path.join('contenuti', filename))  # Specifica il percorso dove salvare il file

    nuovo_post = posts(
        utente=current_user.username,
        media=filename,
        tipo_post='video',
        data_creazione=datetime.now(),
        testo=contenuto
    )

    try:
        db.session.add(nuovo_post)
        db.session.commit()
        flash('Post di video pubblicato con successo', 'alert alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante la pubblicazione del post: {str(e)}', 'alert alert-danger')

    return render_template('template/home_utente.html')

    ## pubblicazione immagine

@utente.route('/pubblica/immagine/<username>', methods=['POST'])
@login_required
def post_immagine(username):
    file = request.files.get('photo')
    contenuto = request.form.get('contenuto')

    if not file or file.filename == '':
        flash('Nessun file selezionato', 'alert alert-warning')
        return render_template('template/pubblicazione_immagine.html')

    filename = secure_filename(file.filename)
    file.save(os.path.join('contenuti', filename))  # Specifica il percorso dove salvare il file

    nuovo_post = posts(
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

    return render_template('template/home_utente.html')


@utente.route('/elimina_post/<int:post_id>', methods=['DELETE'])
@login_required
def elimina_post(id):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se il post esiste e appartiene all'utente corrente
        cursor.execute("SELECT * FROM posts WHERE id = ? AND utente = ?", (id, current_user))
        post = cursor.fetchone()
        
        if post is None:
            return jsonify({"message": "Post non trovato o non autorizzato"}), 404

        # Elimina i commenti associati al post
        cursor.execute("DELETE FROM post_comments WHERE id = ?", (id,))

        # Elimina i like associati al post
        cursor.execute("DELETE FROM post_likes WHERE id = ?", (id,))
        
        # Elimina il post
        cursor.execute("DELETE FROM posts WHERE id = ?", (id,))
        
        conn.commit()
        return jsonify({"message": "Post eliminato con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('profilo_io.html')

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

@utente.route('/elimina_commento/<int:comment_id>', methods=['DELETE'])
@login_required
def elimina_commento(id):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se il commento esiste e appartiene all'utente corrente
        cursor.execute("SELECT * FROM post_comments WHERE id = ? AND utentec = ?", (id, current_user))
        commento = cursor.fetchone()
        
        if commento is None:
            return jsonify({"message": "Commento non trovato o non autorizzato"}), 404
        
        # Elimina il commento
        cursor.execute("DELETE FROM post_comments WHERE id = ?", (id))
        
        conn.commit()
        return jsonify({"message": "Commento eliminato con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('commenti.html', user=utente)

#------------------------------ inserimento mi piace -------------------------------#

@utente.route('/mi_piace/<int:post_id>', methods=['POST'])
@login_required
def mi_piace(post_id):
    post = posts.query.get(post_id)

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

@utente.route('/<int:post_id>', methods=['DELETE'])
@login_required
def elimina_mi_piace(post_id):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se il commento esiste e appartiene all'utente corrente
        cursor.execute("SELECT * FROM post_likes WHERE posts_id = ? AND username = ?", (post_id, current_user))
        commento = cursor.fetchone()
        
        if commento is None:
            return jsonify({"message": "Commento non trovato o non autorizzato"}), 404
        
        # Elimina il commento
        cursor.execute("DELETE FROM post_likes WHERE post_id = ?", (post_id))
        
        conn.commit()
        return jsonify({"message": "Like eliminato con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('home_utente.html', user=current_user)

#------------------------------ seguire e accettare -------------------------------#

    # inviare una richiesta ad una persona

@utente.route('/richieste/<string:utente>', methods=['POST'])
@login_required
def invia_richiesta(utente):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Inserisci una nuova richiesta di amicizia
        cursor.execute("""
            INSERT INTO amici (io_utente, user_amico, stato_richiesta)
            VALUES (?, ?, ?)
        """, (current_user, utente, 'in_attesa'))
        
        conn.commit()
        return jsonify({"message": "Richiesta di amicizia inviata con successo"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"message": "Errore: richiesta di amicizia già inviata o utente non esistente"}), 400

    finally:
        conn.close()
        return render_template('profilo_amico.html', user=utente)

    # accettare una richiesta

@utente.route('/richieste/<string:utente>', methods=['POST'])
@login_required
def accetta_richiesta(utente):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Aggiorna lo stato della richiesta di amicizia
        cursor.execute("""
            UPDATE amici
            SET stato_richiesta = ?
            WHERE io_utente = ? AND user_amico = ? AND stato_richiesta = ?
        """, ('accettata', utente, current_user, 'in_attesa'))
        
        if cursor.rowcount == 0:
            return jsonify({"message": "Errore: richiesta di amicizia non trovata o già accettata"}), 400
        
        conn.commit()
        return jsonify({"message": "Richiesta di amicizia accettata con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('profilo_amico.html', user=utente)

    #rifiuta richiesta

@utente.route('/richieste/<string:utente>', methods=['POST'])
@login_required
def rifiuta_richiesta(utente):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Aggiorna lo stato della richiesta di amicizia
        cursor.execute("""
            DELETE FROM amici 
            WHERE stato= ? AND user_amico= ? AND io_utente=?
        """, ('in attesa', utente, current_user))
        
        if cursor.rowcount == 0:
            return jsonify({"message": "Errore: richiesta di amicizia non trovata o già accettata"}), 400
        
        conn.commit()
        return jsonify({"message": "Richiesta di amicizia rifiutata con successo :) "}), 200

    except sqlite3.Error as e:
        return jsonify({"message": "Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('profilo_amico.html', user=utente)


#------------------------------ ricerca utente -------------------------------#

@utente.route('/cerca_utente', methods=['GET', 'POST'])
@login_required
def cerca_utente():
    if request.method == 'POST':
        search_term = request.form.get('search_term', '')
        risultati_ricerca = User.query.filter(User.username.ilike(f'%{search_term}%')).all()
        return render_template('risultati_ricerca.html', risultati=risultati_ricerca, search_term=search_term)
    
    return render_template('cerca_utente.html')

#------------------------------- rimuovere amici ---------------------------------#

    # funzione per rimuovere persone dalle persone che ti seguono

@utente.route('/rimuovi_follower/<string:follower>', methods=['DELETE'])
@login_required
def rimuovi_follower(follower):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se il follower esiste e sta seguendo l'utente corrente
        cursor.execute("""
            SELECT * FROM amici WHERE user_amico = ? AND io_utente = ?
        """, (current_user, follower))
        follow = cursor.fetchone()
        
        if follow is None:
            return jsonify({"message": "Follower non trovato"}), 404

        # Rimuovi il follower
        cursor.execute("""
            DELETE FROM amici WHERE user_amico = ? AND io_utente = ?
        """, (follower, current_user))
        
        conn.commit()
        return jsonify({"message": "Follower rimosso con successo"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('lista_amici.html', user=current_user)

    # funzione per smettere di seguire persone

@utente.route('/smetti_di_seguire/<string:followed>', methods=['DELETE'])
@login_required
def smetti_di_seguire(follower):
    current_user = request.json['current_user']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se l'utente corrente sta seguendo la persona specificata
        cursor.execute("""
            SELECT * FROM amici WHERE user_amico = ? AND io_utente = ?
        """, (follower, current_user))
        follow = cursor.fetchone()
        
        if follow is None:
            return jsonify({"message": "Non stai seguendo questa persona"}), 404

        # Smetti di seguire la persona
        cursor.execute("""
            DELETE FROM amici WHERE user_amico = ? AND io_utente = ?
        """, (follower, current_user))
        
        conn.commit()
        return jsonify({"message": "Hai smesso di seguire questa persona"}), 200

    except sqlite3.Error as e:
        return jsonify({"message": f"Errore nel database: {e}"}), 500

    finally:
        conn.close()
        return render_template('profilo_amici.html', user=follower)