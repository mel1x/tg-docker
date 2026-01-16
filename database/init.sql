CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS user_messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username VARCHAR(100),
    message_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Тестовые данные
INSERT INTO users (user_id, username, first_name, last_name) 
VALUES (123456, 'test_user', 'Иван', 'Петров')
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_messages (user_id, username, message_text) 
VALUES (123456, 'test_user', 'Первое тестовое сообщение')
ON CONFLICT DO NOTHING;
