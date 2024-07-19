-- Inserimento dati nella tabella users
INSERT INTO users (username, immagine, nome, cognome, password_hash, email, sesso, eta, ruolo)
VALUES
('user1', NULL, 'Mario', 'Rossi', 'password123', 'mario@email.com', 'maschio', 30, 'utente'),
('user2', NULL, 'Giulia', 'Verdi', 'securepwd', 'giulia@email.com', 'femmina', 25, 'utente'),
('advertiser1', NULL, 'Alessandro', 'Bianchi', 'topsecret', 'alessandro@email.com', 'maschio', 35, 'pubblicitari');

-- Inserimento dati nella tabella interessi
INSERT INTO interessi (nome)
VALUES
('Sport'),
('Musica'),
('Viaggi');

-- Inserimento dati nella tabella user_interessi
INSERT INTO user_interessi (username, id_interessi)
VALUES
('user1', 1),  -- Mario Rossi è interessato allo Sport
('user1', 2),  -- Mario Rossi è interessato alla Musica
('user2', 2),  -- Giulia Verdi è interessata alla Musica
('user2', 3);  -- Giulia Verdi è interessata ai Viaggi

-- Inserimento dati nella tabella amici
INSERT INTO amici (io_utente, user_amico, stato)
VALUES
('user1', 'user2', 'accettato'),
('user2', 'user1', 'accettato');

-- Inserimento dati nella tabella posts
INSERT INTO posts (utente, media, tipo_post, testo)
VALUES
('user1', NULL, 'immagini', 'Nuova foto di viaggio!'),
('user2', NULL, 'video', 'Guardate questo video interessante!');

-- Inserimento dati nella tabella post_comments
INSERT INTO post_comments (post_id, utentec, content)
VALUES
(1, 'user2', 'Bellissima foto!'),
(2, 'user1', 'Mi piace molto il video.');

-- Inserimento dati nella tabella post_likes
INSERT INTO post_likes (post_id, username)
VALUES
(1, 'user2'),
(2, 'user1');

-- Inserimento dati nella tabella annunci
INSERT INTO annunci (id, advertiser, tipo_post, sesso_target, eta_target, interesse_target, inizio, fine)
VALUES
(1, 'advertiser1', 'immagini', 'maschio', 25, 1, CURRENT_TIMESTAMP, CURRENT_DATE),
(2, 'advertiser1', 'video', 'femmina', 30, 2, CURRENT_TIMESTAMP, '2024-08-31');

-- Inserimento dati nella tabella annunci_likes
INSERT INTO annunci_likes (annuncio_id, username)
VALUES
(1, 'user1'),
(2, 'user2');

-- Inserimento dati nella tabella annunci_comments
INSERT INTO annunci_comments (annuncio_id, utentec, content)
VALUES
(1, 'user1', 'Interessante!'),
(2, 'user2', 'Mi piace questo annuncio.');

-- Inserimento dati nella tabella target
INSERT INTO target (sesso, eta, interesse)
VALUES
('maschio', 25, 1),
('femmina', 30, 2);
