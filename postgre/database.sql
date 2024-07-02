CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    is_advertiser BOOLEAN DEFAULT FALSE
);

CREATE TABLE friendships (
    user_id INTEGER REFERENCES users(id),
    friend_id INTEGER REFERENCES users(id),
    PRIMARY KEY (user_id, friend_id)
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content TEXT,
    post_type VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    user_id INTEGER REFERENCES users(id),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ads (
    id SERIAL PRIMARY KEY,
    advertiser_id INTEGER REFERENCES users(id),
    content TEXT,
    targeting_criteria TEXT,
    budget INTEGER,
    clicks INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 0
);

CREATE TABLE clicks (
    ad_id INTEGER REFERENCES ads(id),
    user_id INTEGER REFERENCES users(id),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
