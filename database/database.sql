CREATE TYPE ruolo AS ENUM('utente', 'pubblicitari');
CREATE TYPE tipo_post AS ENUM('immagini', 'video', 'testo');
CREATE TYPE sesso AS ENUM('maschio', 'femmina', 'altro');


CREATE TABLE users (
    id_utente SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    immagine BYTEA,  -- Utilizzo di BYTEA invece di BLOB su PostgreSQL
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    sesso sesso,
    eta INTEGER NOT NULL,
    ruolo ruolo
);


CREATE TABLE interessi (
    id_interessi SERIAL PRIMARY KEY,
    nome VARCHAR(50)
);

CREATE TABLE user_interessi (
    utente_id INTEGER REFERENCES users(id_utente),
    id_interessi INTEGER REFERENCES interessi(id_interessi),
    PRIMARY KEY (utente_id, id_interessi)
);


CREATE TABLE amici (
    id_amicizia SERIAL PRIMARY KEY,
    io_utente INTEGER REFERENCES users(id_utente),
    user_amico INTEGER REFERENCES users(id_utente),
    seguito_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    utente INTEGER REFERENCES users(id_utente),
    media BYTEA,
    tipo_post tipo_post,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    testo TEXT
);



CREATE TABLE post_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    utente_id INTEGER REFERENCES users(id_utente),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE post_likes (
    post_id INTEGER REFERENCES posts(id),
    utente_id INTEGER REFERENCES users(id_utente),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, utente_id)
);


CREATE TABLE annunci (
    id SERIAL PRIMARY KEY,
    advertiser_id INTEGER REFERENCES users(id_utente),
    tipo_post tipo_post,
    sesso_target sesso,
    eta_target INTEGER,
    interesse_target INTEGER REFERENCES interessi(id_interessi),
    inizio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fine DATE
);

CREATE TABLE annunci_likes (
    annuncio_id INTEGER REFERENCES annunci(id),
    utente_id INTEGER REFERENCES users(id_utente),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (annuncio_id, utente_id)
);


CREATE TABLE annunci_comments (
    id SERIAL PRIMARY KEY,
    annuncio_id INTEGER REFERENCES annunci(id),
    utente_id INTEGER REFERENCES users(id_utente),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE target (
    id SERIAL PRIMARY KEY,
    sesso sesso,
    eta INTEGER,
    interesse INTEGER REFERENCES interessi(id_interessi)
);

CREATE TABLE messaggi (
    id SERIAL PRIMARY KEY,
    testo TEXT NOT NULL,
    mittente_id INTEGER NOT NULL,
    destinatario_id INTEGER NOT NULL,
    creato_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (mittente_id) REFERENCES users(id_utente) ON DELETE CASCADE,
    FOREIGN KEY (destinatario_id) REFERENCES users(id_utente) ON DELETE CASCADE
);




/*TRIGGHER*/

/*---------------------------------------------------------------------------*/

-- Trigger per cancellare i commenti e i like associati a un post quando il post viene cancellato
CREATE OR REPLACE FUNCTION cascade_delete_post()
RETURNS TRIGGER AS $$
BEGIN
   DELETE FROM post_comments WHERE post_id = OLD.id;
   DELETE FROM post_likes WHERE post_id = OLD.id;
   RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER delete_post_cascade
BEFORE DELETE ON posts
FOR EACH ROW EXECUTE FUNCTION cascade_delete_post();



/*---------------------------------------------------------------------------*/

-- Trigger per aggiornare automaticamente il timestamp di modifica
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_posts_timestamp
BEFORE UPDATE ON posts
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_comments_timestamp
BEFORE UPDATE ON post_comments
FOR EACH ROW EXECUTE FUNCTION update_timestamp();


/*---------------------------------------------------------------------------*/

-- Trigger per cancellare i commenti e i like associati a un annuncio quando l'annuncio viene cancellato
CREATE OR REPLACE FUNCTION cascade_delete_annuncio()
RETURNS TRIGGER AS $$
BEGIN
   DELETE FROM annunci_comments WHERE annuncio_id = OLD.id;
   DELETE FROM annunci_likes WHERE annuncio_id = OLD.id;
   RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER delete_annuncio_cascade
BEFORE DELETE ON annunci
FOR EACH ROW EXECUTE FUNCTION cascade_delete_annuncio();


/*---------------------------------------------------------------------------*/

-- Trigger per garantire che l'età dell'utente sia maggiore di 0
CREATE OR REPLACE FUNCTION validate_user_age()
RETURNS TRIGGER AS $$
BEGIN
   IF NEW.eta <= 0 THEN
      RAISE EXCEPTION 'L''età deve essere maggiore di 0';
   END IF;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_user_age
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION validate_user_age();

/*---------------------------------------------------------------------------*/

-- Trigger per rimuovere tutte le relazioni di follower quando un utente viene cancellato
CREATE OR REPLACE FUNCTION cascade_delete_user_followers()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM user_follows WHERE follower_id = OLD.id_utente;
    DELETE FROM user_follows WHERE followed_id = OLD.id_utente;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER delete_user_followers_cascade
BEFORE DELETE ON users
FOR EACH ROW EXECUTE FUNCTION cascade_delete_user_followers();