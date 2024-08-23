-- Inserimento utenti
INSERT INTO users (id_utente, username, immagine, nome, cognome, password_, email, sesso, eta, ruolo, bio) VALUES
(1, 'utente1', 'immagine1.jpg', 'Mario', 'Rossi', 'password123', 'mario.rossi@example.com', 'maschio', 25, 'utente', 'Bio di Mario Rossi'),
(2, 'utente2', 'immagine2.jpg', 'Luigi', 'Verdi', 'password456', 'luigi.verdi@example.com', 'maschio', 30, 'utente', 'Bio di Luigi Verdi'),
(3, 'pubblicitario1', 'immagine3.jpg', 'Anna', 'Bianchi', 'password789', 'anna.bianchi@example.com', 'femmina', 28, 'pubblicitari', 'Bio di Anna Bianchi'),
(4, 'utente3', 'immagine4.jpg', 'Marco', 'Neri', 'password321', 'marco.neri@example.com', 'maschio', 22, 'utente', 'Bio di Marco Neri'),
(5, 'utente4', 'immagine5.jpg', 'Giulia', 'Rossi', 'password654', 'giulia.rossi@example.com', 'femmina', 27, 'utente', 'Bio di Giulia Rossi'),
(6, 'utente5', 'immagine7.jpg', 'Clara', 'Blu', 'password987', 'clara.blu@example.com', 'femmina', 29, 'utente', 'Bio di Clara Blu'),
(7, 'utente6', 'immagine8.jpg', 'Davide', 'Gialli', 'password654', 'davide.gialli@example.com', 'maschio', 32, 'utente', 'Bio di Davide Gialli'),
(8, 'pubblicitario2', 'immagine9.jpg', 'Sara', 'Viola', 'password321', 'sara.viola@example.com', 'femmina', 35, 'pubblicitari', 'Bio di Sara Viola'),
(9, 'utente7', 'immagine10.jpg', 'Pietro', 'Aranci', 'password111', 'pietro.aranci@example.com', 'maschio', 26, 'utente', 'Bio di Pietro Aranci'),
(10, 'utente8', 'immagine11.jpg', 'Elena', 'Azzurri', 'password222', 'elena.azzurri@example.com', 'femmina', 31, 'utente', 'Bio di Elena Azzurri');

-- Inserimento interessi
INSERT INTO interessi (id_interessi, nome) VALUES
(1, 'Sport'),
(2, 'Musica'),
(3, 'Tecnologia'),
(4, 'Cucina'),
(5, 'Viaggi'),
(6, 'Libri'),
(7, 'Cinema'),
(8, 'Arte'),
(9, 'Giardinaggio'),
(10, 'Fotografia'),
(11, 'Fai da te'),
(12, 'Moda'),
(13, 'Storia'),
(14, 'Giochi da tavolo');

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
INSERT INTO amici (id_amicizia, io_utente, user_amico) VALUES
(1, 1, 2),
(2, 2, 3),
(3, 3, 4),
(4, 4, 5),
(5, 1, 3),
(6, 2, 4),
(7, 6, 7),
(8, 7, 8),
(9, 8, 9),
(10, 9, 10),
(11, 6, 8),
(12, 7, 9);

-- Inserimento posts
INSERT INTO posts (id, utente, media, tipo_post, testo) VALUES
(1, 1, 'media1.jpg', 'immagini', 'La mia colazione di oggi!'),
(2, 2, 'media2.jpg', 'immagini', 'Un’immagine di Snoopy!'),
(3, 3, 'media3.jpg', 'immagini', 'Adoro questo personaggio!'),
(4, 4, 'media4.jpg', 'immagini', 'Un bel paesaggio che ho fotografato.'),
(5, 5, 'media5.jpg', 'immagini', 'Tempo di relax.'),
(6, 6, 'media6.jpg', 'immagini', 'Il mio caffè mattutino!'),
(7, 7, 'media7.jpg', 'immagini', 'Il mio nuovo gatto!'),
(8, 8, 'media8.jpg', 'immagini', 'Consiglio di lettura del mese.'),
(9, 9, 'media9.jpg', 'immagini', 'Una fantastica escursione!'),
(10, 10, 'media10.jpg', 'immagini', 'Un tramonto mozzafiato!');

-- Inserimento post_comments
INSERT INTO post_comments (id, post_id, utente_id, content) VALUES
(1, 1, 2, 'Che buona!'),
(2, 2, 1, 'Snoopy è il migliore!'),
(3, 3, 4, 'Anche a me piace!'),
(4, 4, 3, 'Bella foto!'),
(5, 5, 2, 'Concordo, relax totale!'),
(6, 6, 7, 'Che bello iniziare la giornata così!'),
(7, 7, 8, 'Adoro i gatti, troppo carino!'),
(8, 8, 9, 'Grazie per il consiglio, lo leggerò.'),
(9, 9, 10, 'Sembra un bel posto per rilassarsi.'),
(10, 10, 6, 'Wow, che tramonto!');

-- Inserimento post_likes
INSERT INTO post_likes (post_id, utente_id) VALUES
(1, 3),
(2, 4),
(3, 5),
(4, 1),
(5, 2),
(6, 8),
(7, 9),
(8, 10),
(9, 6),
(10, 7);

-- Inserimento annunci
INSERT INTO annunci (id, advertiser_id, tipo_post, sesso_target, eta_target, interesse_target, inizio, fine, media, testo, titolo, link) VALUES
(1, 3, 'immagini', 'tutti', 18, 1, CURRENT_TIMESTAMP, '2024-12-31', 'media_annuncio1.jpg', 'Scopri il nostro nuovo prodotto!', 'Promozione Speciale', 'http://example.com/promo1'),
(2, 3, 'immagini', 'femmina', 25, 2, CURRENT_TIMESTAMP, '2024-11-30', 'media_annuncio2.jpg', 'Ascolta la nostra nuova playlist!', 'Nuova Musica', 'http://example.com/music'),
(3, 3, 'testo', 'maschio', 30, 3, CURRENT_TIMESTAMP, '2024-10-31', NULL, 'Esplora nuove destinazioni!', 'Viaggi Avventura', 'http://example.com/travel'),
(4, 8, 'immagini', 'tutti', 25, 6, CURRENT_TIMESTAMP, '2024-12-31', 'media_annuncio3.jpg', 'Scopri i nostri nuovi libri!', 'Novità in libreria', 'http://example.com/books'),
(5, 8, 'immagini', 'maschio', 28, 1, CURRENT_TIMESTAMP, '2024-11-30', 'media_annuncio4.jpg', 'Unisciti al nostro club di basket!', 'Sport per tutti', 'http://example.com/basket'),
(6, 8, 'testo', 'femmina', 32, 2, CURRENT_TIMESTAMP, NULL, 'Entra nel mondo della musica!', 'Passione musicale', 'http://example.com/musicworld');

-- Inserimento annunci_likes
INSERT INTO annunci_likes (annuncio_id, utente_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 6),
(5, 7),
(6, 9);

-- Inserimento annunci_comments
INSERT INTO annunci_comments (id, annuncio_id, utente_id, content) VALUES
(1, 1, 2, 'Interessante!'),
(2, 2, 3, 'Mi piace questa canzone!'),
(3, 3, 1, 'Voglio viaggiare di più!'),
(4, 4, 10, 'Adoro leggere, ci darò un occhiata!'),
(5, 5, 6, 'Basket, perfetto per rimanere in forma!'),
(6, 6, 7, 'Sempre amato la musica, fantastico!');

-- Inserimento annunci_clicks
INSERT INTO annunci_clicks (annuncio_id, utente_id) VALUES
(1, 3),
(2, 1),
(3, 2),
(4, 9),
(5, 10),
(6, 8);

-- Inserimento messaggi
INSERT INTO messaggi (id, testo, mittente_id, destinatario_id, creato_at, postinviato) VALUES
(1, 'Ciao, come stai?', 1, 2, CURRENT_TIMESTAMP, NULL),
(2, 'Hai visto il nuovo post?', 2, 3, CURRENT_TIMESTAMP, 1),
(3, 'Bella foto!', 3, 4, CURRENT_TIMESTAMP, 4),
(4, 'Grazie! Come va?', 4, 1, CURRENT_TIMESTAMP, NULL),
(5, 'Ci vediamo stasera?', 5, 1, CURRENT_TIMESTAMP, NULL),
(6, 'Ti piace il nuovo libro che ho comprato?', 6, 7, CURRENT_TIMESTAMP, NULL),
(7, 'Dovremmo provare a giocare insieme a basket!', 7, 8, CURRENT_TIMESTAMP, NULL),
(8, 'Grazie per il consiglio musicale!', 8, 9, CURRENT_TIMESTAMP, NULL),
(9, 'Hai visto il tramonto ieri?', 9, 10, CURRENT_TIMESTAMP, NULL),
(10, 'Che bel gatto!', 10, 6, CURRENT_TIMESTAMP, NULL);

-- Inserimento annuncibudget
INSERT INTO annuncibudget (annuncio_id, budget, budget_rimanente) VALUES
(1, 5000.0, 5000.0),
(2, 3000.0, 3000.0),
(3, 4000.0, 4000.0),
(4, 2000.0, 2000.0),
(5, 3500.0, 3500.0),
(6, 4500.0, 4500.0);
