-- Inserimento utenti
INSERT INTO users (id_utente, username, immagine, nome, cognome, password_, email, sesso, eta, ruolo, bio) VALUES
(1, 'utente1', 'fotoprofilo.jpg', 'Mario', 'Rossi', 'password123', 'mario.rossi@example.com', 'maschio', 25, 'utente', 'Bio di Mario Rossi'),
(2, 'utente2', 'cat.jpg', 'Luigi', 'Verdi', 'password456', 'luigi.verdi@example.com', 'maschio', 30, 'utente', 'Bio di Luigi Verdi'),
(3, 'pubblicitario1', 'pixel.jpg', 'Anna', 'Bianchi', 'password789', 'anna.bianchi@example.com', 'femmina', 28, 'pubblicitari', 'Bio di Anna Bianchi'),
(4, 'utente3', 'poyolol.jpg', 'Marco', 'Neri', 'password321', 'marco.neri@example.com', 'maschio', 22, 'utente', 'Bio di Marco Neri'),
(5, 'utente4', 'rest.jpg', 'Giulia', 'Rossi', 'password654', 'giulia.rossi@example.com', 'femmina', 27, 'utente', 'Bio di Giulia Rossi');

-- Inserimento interessi
INSERT INTO interessi (nome)
VALUES 
('Sport'),
('Musica'),
('Tecnologia'),
('Cucina'),
('Viaggi'),
('Libri'),
('Cinema'),
('Arte'),
('Giardinaggio'),
('Fotografia'),
('Fai da te'),
('Moda'),
('Storia'),
('Giochi da tavolo');


-- Inserimento user_interessi
INSERT INTO user_interessi (utente_id, id_interessi) VALUES
(1, 1),
(1, 2),
(2, 3),
(2, 4),
(3, 5),
(4, 1),
(4, 5),
(5, 2),
(5, 3);

-- Inserimento amici
INSERT INTO amicizia (id_amicizia, io_utente, user_amico) VALUES
(1, 1, 2),
(2, 2, 3),
(3, 3, 4),
(4, 4, 5),
(5, 1, 3),
(6, 2, 4);

-- Inserimento posts
INSERT INTO posts (id, utente, media, tipo_post, testo) VALUES
(1, 1, 'colazione.jpg', 'immagini', 'La mia colazione di oggi!'),
(2, 2, 'snoopy.jpg', 'immagini', 'Un’immagine di Snoopy!'),
(3, 3, 'POYO.jpg', 'immagini', 'Adoro questo personaggio!'),
(4, 4, 'paesaggio.jpg', 'immagini', 'Un bel paesaggio che ho fotografato.'),
(5, 5, 'rest.jpg', 'immagini', 'Tempo di relax.');

-- Inserimento post_comments
INSERT INTO post_comments (id, post_id, utente_id, content) VALUES
(1, 1, 2, 'Che buona!'),
(2, 2, 1, 'Snoopy è il migliore!'),
(3, 3, 4, 'Anche a me piace!'),
(4, 4, 3, 'Bella foto!'),
(5, 5, 2, 'Concordo, relax totale!');

-- Inserimento post_likes
INSERT INTO post_likes (post_id, utente_id) VALUES
(1, 3),
(2, 4),
(3, 5),
(4, 1),
(5, 2);

-- Inserimento annunci
INSERT INTO annunci (id, advertiser_id, tipo_post, sesso_target, eta_target, interesse_target, inizio, fine, media, testo, titolo, link) VALUES
(1, 3, 'video', 'tutti', 18, 1, CURRENT_TIMESTAMP, '2024-12-31', 'paesaggio.jpg', 'Scopri il nostro nuovo prodotto!', 'Promozione Speciale', 'http://example.com/promo1'),
(2, 3, 'immagini', 'femmina', 25, 2, CURRENT_TIMESTAMP, '2024-11-30', 'POYO.jpg', 'Ascolta la nostra nuova playlist!', 'Nuova Musica', 'http://example.com/music'),
(3, 3, 'testo', 'maschio', 30, 3, CURRENT_TIMESTAMP, '2024-10-31', NULL, 'Esplora nuove destinazioni!', 'Viaggi Avventura', 'http://example.com/travel');

-- Inserimento annunci_likes
INSERT INTO annunci_likes (annuncio_id, utente_id) VALUES
(1, 1),
(2, 2),
(3, 3);

-- Inserimento annunci_comments
INSERT INTO annunci_comments (id, annuncio_id, utente_id, content) VALUES
(1, 1, 2, 'Interessante!'),
(2, 2, 3, 'Mi piace questa canzone!'),
(3, 3, 1, 'Voglio viaggiare di più!');

-- Inserimento annunci_clicks
INSERT INTO annunci_clicks (annuncio_id, utente_id) VALUES
(1, 3),
(2, 1),
(3, 2);

-- Inserimento messaggi
INSERT INTO messaggi (id, testo, mittente_id, destinatario_id, creato_at, postinviato) VALUES
(1, 'Ciao, come stai?', 1, 2, CURRENT_TIMESTAMP, NULL),
(2, 'Hai visto il nuovo post?', 2, 3, CURRENT_TIMESTAMP, 1),
(3, 'Bella foto!', 3, 4, CURRENT_TIMESTAMP, 4),
(4, 'Grazie! Come va?', 4, 1, CURRENT_TIMESTAMP, NULL),
(5, 'Ci vediamo stasera?', 5, 1, CURRENT_TIMESTAMP, NULL);
