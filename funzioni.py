from flask_socketio import SocketIO
socketio = SocketIO(app)
@app.route('/insight')
@login_required
def insight():
    likes = get_likes_per_month(db.session, current_user.id_utente)
    comments = get_comments_per_month(db.session, current_user.id_utente)
    followers = get_followers_per_month(db.session, current_user.id_utente)
    
    return render_template('insight.html', likes=likes, comments=comments, followers=followers)

# Emit an update when a like is added
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Emit initial data to the client
    emit_initial_data()

@socketio.on('new_like')
def handle_new_like(data):
    # Update the database and fetch the updated data
    likes = get_likes_per_month(db.session, current_user.id_utente)
    comments = get_comments_per_month(db.session, current_user.id_utente)
    followers = get_followers_per_month(db.session, current_user.id_utente)
    
    # Emit updated data to the client
    socketio.emit('update', {
        'likes': likes,
        'comments': comments,
        'followers': followers
    })

def emit_initial_data():
    # This function emits initial data to the client when they connect
    likes = get_likes_per_month(db.session, current_user.id_utente)
    comments = get_comments_per_month(db.session, current_user.id_utente)
    followers = get_followers_per_month(db.session, current_user.id_utente)
    
    socketio.emit('update', {
        'likes': likes,
        'comments': comments,
        'followers': followers
    })

def get_likes_per_month(session, user_id):
    start_date = datetime.today().replace(day=1)
    end_date = (start_date + timedelta(days=32)).replace(day=1)
    
    results = session.query(
        func.date_trunc('day', PostLikes.clicked_at).label('date'),
        func.count().label('count')
    ).filter(
        PostLikes.utente_id == user_id,
        PostLikes.clicked_at >= start_date,
        PostLikes.clicked_at < end_date
    ).group_by('date').order_by('date').all()
    
    # Initialize list for daily counts
    daily_counts = [0] * (end_date.day)
    for date, count in results:
        day = date.day
        if 1 <= day <= len(daily_counts):
            daily_counts[day - 1] = count
    
    return daily_counts

def get_comments_per_month(session, user_id):
    start_date = datetime.today().replace(day=1)
    end_date = (start_date + timedelta(days=32)).replace(day=1)
    
    results = session.query(
        func.date_trunc('day', PostComments.created_at).label('date'),
        func.count().label('count')
    ).filter(
        PostComments.utente_id == user_id,
        PostComments.created_at >= start_date,
        PostComments.created_at < end_date
    ).group_by('date').order_by('date').all()
    
    # Initialize list for daily counts
    daily_counts = [0] * (end_date.day)
    for date, count in results:
        day = date.day
        if 1 <= day <= len(daily_counts):
            daily_counts[day - 1] = count
    
    return daily_counts

def get_followers_per_month(session, user_id):
    start_date = datetime.today().replace(day=1)
    end_date = (start_date + timedelta(days=32)).replace(day=1)
    
    results = session.query(
        func.date_trunc('day', Amici.seguito_at).label('date'),
        func.count().label('count')
    ).filter(
        Amici.user_amico == user_id,
        Amici.seguito_at >= start_date,
        Amici.seguito_at < end_date
    ).group_by('date').order_by('date').all()
    
    # Initialize list for daily counts
    daily_counts = [0] * (end_date.day)
    for date, count in results:
        day = date.day
        if 1 <= day <= len(daily_counts):
            daily_counts[day - 1] = count
    
    return daily_counts

def add_like(post_id, user_id):
    # Crea un nuovo like
    new_like = PostLikes(post_id=post_id, utente_id=user_id, clicked_at=datetime.utcnow())
    
    # Aggiungi il like al database
    db.session.add(new_like)
    db.session.commit()
    
    # Emmetti l'evento per aggiornare i grafici in tempo reale
    update_graphs(user_id)

def add_comment(post_id, user_id, content):
    # Crea un nuovo commento
    new_comment = PostComments(post_id=post_id, utente_id=user_id, content=content, created_at=datetime.utcnow())
    
    # Aggiungi il commento al database
    db.session.add(new_comment)
    db.session.commit()
    
    # Emmetti l'evento per aggiornare i grafici in tempo reale
    update_graphs(user_id)

def add_follow(following_user_id, follower_user_id):
    # Crea un nuovo follow
    new_follow = Amici(user_amico=following_user_id, utente_id=follower_user_id, seguito_at=datetime.utcnow())
    
    # Aggiungi il follow al database
    db.session.add(new_follow)
    db.session.commit()
    
    # Emmetti l'evento per aggiornare i grafici in tempo reale
    update_graphs(follower_user_id)

def update_graphs(user_id):
    likes = get_likes_per_month(db.session, user_id)
    comments = get_comments_per_month(db.session, user_id)
    followers = get_followers_per_month(db.session, user_id)
    
    socketio.emit('update', {
        'likes': likes,
        'comments': comments,
        'followers': followers
    })

if __name__ == '__main__':
    socketio.run(app, debug=True)