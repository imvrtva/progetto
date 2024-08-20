CREATE TYPE ruolo AS ENUM('utente', 'pubblicitari');
CREATE TYPE tipo_post AS ENUM('immagini', 'video', 'testo');
CREATE TYPE sesso AS ENUM('maschio', 'femmina', 'altro', 'tutti');

CREATE TABLE users (
    id_utente SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    immagine VARCHAR(100),  -- Modificato per corrispondere a immagine VARCHAR
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    password_ VARCHAR(150) NOT NULL,  -- Modificato per corrispondere a password_ VARCHAR
    email VARCHAR(150) UNIQUE NOT NULL,
    sesso sesso,
    eta INTEGER NOT NULL,
    ruolo ruolo,
    bio VARCHAR(250)  -- Aggiunto per corrispondere a bio
);

CREATE TABLE interessi (
    id_interessi SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL  -- Aggiunto NOT NULL per corrispondere al modello
);

CREATE TABLE user_interessi (
    utente_id INTEGER REFERENCES users(id_utente),
    id_interessi INTEGER REFERENCES interessi(id_interessi),
    PRIMARY KEY (utente_id, id_interessi)
);

CREATE TABLE amicizia (
    id_amicizia SERIAL PRIMARY KEY,
    io_utente INTEGER REFERENCES users(id_utente),
    user_amico INTEGER REFERENCES users(id_utente),
    seguito_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    utente INTEGER REFERENCES users(id_utente),
    media VARCHAR(255),  -- Modificato per corrispondere a media VARCHAR
    tipo_post tipo_post,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    testo TEXT
);

CREATE TABLE post_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    utente_id INTEGER REFERENCES users(id_utente),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE post_likes (
    post_id INTEGER REFERENCES posts(id),
    utente_id INTEGER REFERENCES users(id_utente),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (post_id, utente_id)
);

CREATE TABLE annunci (
    id SERIAL PRIMARY KEY,
    advertiser_id INTEGER REFERENCES users(id_utente),
    tipo_post tipo_post,
    sesso_target sesso,
    eta_target INTEGER NOT NULL,
    interesse_target INTEGER REFERENCES interessi(id_interessi),
    inizio TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fine DATE,
    media VARCHAR(255),
    testo VARCHAR(255),
    titolo VARCHAR(255),  -- Aggiunto titolo
    link VARCHAR(200)  -- Aggiunto link
);

CREATE TABLE annunci_likes (
    annuncio_id INTEGER REFERENCES annunci(id),
    utente_id INTEGER REFERENCES users(id_utente),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (annuncio_id, utente_id)
);

CREATE TABLE annunci_comments (
    id SERIAL PRIMARY KEY,
    annuncio_id INTEGER REFERENCES annunci(id),
    utente_id INTEGER REFERENCES users(id_utente),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE annunci_clicks (
    annuncio_id INTEGER REFERENCES annunci(id),
    utente_id INTEGER REFERENCES users(id_utente),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (annuncio_id, utente_id)
);

CREATE TABLE messaggi (
    id SERIAL PRIMARY KEY,
    testo TEXT NOT NULL,
    mittente_id INTEGER NOT NULL REFERENCES users(id_utente) ON DELETE CASCADE,
    destinatario_id INTEGER NOT NULL REFERENCES users(id_utente) ON DELETE CASCADE,
    creato_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    postinviato INTEGER REFERENCES posts(id)  -- Aggiunto riferimento a postinviato
);

CREATE TABLE annunci_budget (
    id  SERIAL PRIMARY KEY,
    annuncio_id INTEGER NOT NULL UNIQUE,
    budget_totale FLOAT NOT NULL,
    budget_rimanente FLOAT NOT NULL,
    FOREIGN KEY (annuncio_id) REFERENCES annunci(id)
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

/*---------------------------------------------------------------------------*/

--Trigger per aggiornare seguito_at nella tabella amici quando viene creata una nuova amicizia:
CREATE OR REPLACE FUNCTION update_seguito_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.seguito_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_seguito_at
BEFORE INSERT ON amici
FOR EACH ROW
EXECUTE FUNCTION update_seguito_at();

/*---------------------------------------------------------------------------*/

--Trigger per aggiornare created_at nella tabella post_comments e annunci_comments quando viene aggiunto un nuovo commento:
CREATE OR REPLACE FUNCTION update_created_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.created_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_post_comment_created_at
BEFORE INSERT ON post_comments
FOR EACH ROW
EXECUTE FUNCTION update_created_at();

CREATE TRIGGER set_annuncio_comment_created_at
BEFORE INSERT ON annunci_comments
FOR EACH ROW
EXECUTE FUNCTION update_created_at();

/*---------------------------------------------------------------------------*/

--trigger per assicurarsi che l'età sia un valore positivo nella tabella users:
CREATE OR REPLACE FUNCTION check_eta()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.eta <= 0 THEN
        RAISE EXCEPTION 'L''età deve essere un valore positivo';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_eta_positive
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION check_eta();

/*---------------------------------------------------------------------------*/

--Trigger per garantire che fine sia sempre successiva a inizio nella tabella annunci:
CREATE OR REPLACE FUNCTION check_annuncio_dates()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fine <= NEW.inizio THEN
        RAISE EXCEPTION 'La data di fine deve essere successiva alla data di inizio';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_dates
BEFORE INSERT OR UPDATE ON annunci
FOR EACH ROW
EXECUTE FUNCTION check_annuncio_dates();

/*---------------------------------------------------------------------------*/

--Trigger per prevenire la creazione di amicizie duplicate nella tabella amici:
CREATE OR REPLACE FUNCTION prevent_duplicate_amicizia()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM amici WHERE (io_utente = NEW.io_utente AND user_amico = NEW.user_amico) OR (io_utente = NEW.user_amico AND user_amico = NEW.io_utente)) THEN
        RAISE EXCEPTION 'Questa amicizia già esiste';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_duplicate_amicizia
BEFORE INSERT ON amici
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_amicizia();

