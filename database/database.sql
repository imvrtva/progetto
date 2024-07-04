CREATE TYPE ruolo as ENUM('utente', 'pubblicitari');
CREATE TYPE tipo_post as ENUM('immagini', 'video', 'testi');
CREATE TYPE sesso as ENUM('maschio', 'femmina', 'altro');

CREATE TABLE users (
    username VARCHAR(50) UNIQUE NOT NULL PRIMARY KEY,
    password VARCHAR(100) NOT NULL,
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
    username VARCHAR(50) REFERENCES users(username),
    id_interessi INTEGER REFERENCES interessi(id_interessi),
    PRIMARY KEY (username, id_interessi)
);

CREATE TABLE amici (
    io_utente VARCHAR(50) REFERENCES users(username) PRIMARY KEY,
    user_amico VARCHAR(50) REFERENCES users(username) PRIMARY KEY
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    utente VARCHAR(50) REFERENCES users(username),
    tipo_post tipo_post,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    utentec VARCHAR(50) REFERENCES users(username),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post_likes (
    post_id INTEGER REFERENCES posts(id),
    username VARCHAR(50) REFERENCES users(username),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, username)
);

CREATE TABLE annunci (
    id SERIAL PRIMARY KEY,
    advertiser VARCHAR(50) REFERENCES users(username),
    tipo_post tipo_post,
    sesso_target sesso,
    eta_target INTEGER,
    interesse_target INTEGER REFERENCES interessi(id_interessi),
    inizio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fine DATE
);

CREATE TABLE annunci_likes (
    annuncio_id INTEGER REFERENCES annunci(id),
    username VARCHAR(50) REFERENCES users(username),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (annuncio_id, username)
);

CREATE TABLE annunci_comments (
    id SERIAL PRIMARY KEY,
    annuncio_id INTEGER REFERENCES annunci(id),
    utentec VARCHAR(50) REFERENCES users(username),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE target (
    id SERIAL PRIMARY KEY,
    sesso sesso,
    eta INTEGER,
    interesse INTEGER REFERENCES interessi(id_interessi)
);


/*TRIGGHER*/

/*---------------------------------------------------------------------------*/

-- Trigger per cancellare i commenti e i like associati a un post quando il post viene cancellato
CREATE OR REPLACE FUNCTION cascade_delete_post()
RETURNS TRIGGER AS $$
BEGIN
   DELETE FROM comments WHERE post_id = OLD.id;
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

-- Applicazione del trigger alle tabelle posts e comments
CREATE TRIGGER update_posts_timestamp
BEFORE UPDATE ON posts
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_comments_timestamp
BEFORE UPDATE ON comments
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
    DELETE FROM followers WHERE follower_username = OLD.username;
    DELETE FROM followers WHERE followed_username = OLD.username;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER delete_user_followers_cascade
BEFORE DELETE ON users
FOR EACH ROW EXECUTE FUNCTION cascade_delete_user_followers();
