INSERT INTO users (username, immagine, nome, cognome, password_, email, sesso, eta, ruolo)
VALUES 
('alice', NULL, 'Alice', 'Rossi', 'hashpassword1', 'alice@example.com', 'femmina', 30, 'utente'),
('bob', NULL, 'Bob', 'Bianchi', 'hashpassword2', 'bob@example.com', 'maschio', 25, 'utente'),
('carol', NULL, 'Carol', 'Verdi', 'hashpassword3', 'carol@example.com', 'femmina', 27, 'pubblicitari');


INSERT INTO interessi (nome)
VALUES 
('Sport'),
('Musica'),
('Tecnologia'),
('Cucina');

INSERT INTO user_interessi (utente_id, id_interessi)
VALUES 
(1, 1), -- Alice interessa lo sport
(1, 2), -- Alice interessa la musica
(2, 3), -- Bob interessa la tecnologia
(3, 4); -- Carol interessa la cucina

INSERT INTO amici (io_utente, user_amico, stato)
VALUES 
(1, 2, 'accettato'), -- Alice è amica di Bob
(2, 1, 'accettato'); -- Bob è amico di Alice

INSERT INTO posts (utente, media, tipo_post, testo)
VALUES 
(1, NULL, 'testo', 'Questo è un post di Alice.'),
(2, NULL, 'video', 'Questo è un video di Bob.'),
(1, NULL, 'immagini', 'Questo è un post con immagine di Alice.');

INSERT INTO post_comments (post_id, utente_id, content)
VALUES 
(1, 2, 'Bel post, Alice!'),
(2, 1, 'Interessante video, Bob.');

INSERT INTO post_likes (post_id, utente_id)
VALUES 
(1, 2), -- Bob ha messo like al post di Alice
(2, 1); -- Alice ha messo like al video di Bob

INSERT INTO annunci (advertiser_id, tipo_post, sesso_target, eta_target, interesse_target, inizio, fine)
VALUES 
(3, 'video', 'maschio', 20, 3, '2024-07-01', '2024-07-31'); -- Annuncio pubblicato da Carol, target maschi di 20 anni con interesse in tecnologia

INSERT INTO annunci_likes (annuncio_id, utente_id)
VALUES 
(1, 2); -- Bob ha messo like all'annuncio

INSERT INTO annunci_comments (annuncio_id, utente_id, content)
VALUES 
(1, 1, 'Questo annuncio mi interessa molto.');

INSERT INTO target (sesso, eta, interesse)
VALUES 
('maschio', 20, 3), -- Target per maschi di 20 anni con interesse in tecnologia
('femmina', 30, 1); -- Target per femmine di 30 anni con interesse in sport
