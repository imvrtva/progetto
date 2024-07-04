-- Inserimento utenti
INSERT INTO users (username, password, email, sesso, eta, ruolo) VALUES
('user1', 'password1', 'user1@example.com', 'maschio', 25, 'utente'),
('user2', 'password2', 'user2@example.com', 'femmina', 30, 'utente'),
('user3', 'password3', 'user3@example.com', 'altro', 22, 'pubblicitari'),
('user4', 'password4', 'user4@example.com', 'maschio', 28, 'utente'),
('user5', 'password5', 'user5@example.com', 'femmina', 26, 'pubblicitari');

-- Inserimento interessi
INSERT INTO interessi (nome) VALUES
('Sport'),
('Musica'),
('Tecnologia'),
('Cucina'),
('Viaggi');

-- Inserimento relazioni utente-interessi
INSERT INTO user_interessi (username, id_interessi) VALUES
('user1', 1),
('user1', 2),
('user2', 3),
('user3', 4),
('user4', 5),
('user5', 1);

-- Inserimento relazioni di amicizia
INSERT INTO amici (io_utente, user_amico) VALUES
('user1', 'user2'),
('user2', 'user3'),
('user3', 'user4'),
('user4', 'user5'),
('user5', 'user1');

-- Inserimento post
INSERT INTO posts (utente, tipo_post) VALUES
('user1', 'immagini'),
('user2', 'video'),
('user3', 'testi'),
('user4', 'immagini'),
('user5', 'video');

-- Inserimento commenti ai post
INSERT INTO post_comments (post_id, utentec, content) VALUES
(1, 'user2', 'Bello scatto!'),
(2, 'user3', 'Ottimo video!'),
(3, 'user4', 'Bel post!'),
(4, 'user5', 'Stupenda immagine!'),
(5, 'user1', 'Gran bel video!');

-- Inserimento likes ai post
INSERT INTO post_likes (post_id, username) VALUES
(1, 'user3'),
(2, 'user4'),
(3, 'user5'),
(4, 'user1'),
(5, 'user2');

-- Inserimento annunci
INSERT INTO annunci (advertiser, tipo_post, sesso_target, eta_target, interesse_target, fine) VALUES
('user3', 'video', 'maschio', 25, 1, '2024-12-31'),
('user5', 'immagini', 'femmina', 30, 2, '2024-12-31');

-- Inserimento likes agli annunci
INSERT INTO annunci_likes (annuncio_id, username) VALUES
(1, 'user1'),
(2, 'user2');

-- Inserimento commenti agli annunci
INSERT INTO annunci_comments (annuncio_id, utentec, content) VALUES
(1, 'user4', 'Ottimo annuncio!'),
(2, 'user3', 'Bellissima immagine pubblicitaria!');

-- Inserimento target
INSERT INTO target (sesso, eta, interesse) VALUES
('maschio', 25, 1),
('femmina', 30, 2);
