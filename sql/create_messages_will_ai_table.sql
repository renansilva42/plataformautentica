-- SQL command to create messages table for Will AI
CREATE TABLE IF NOT EXISTS messages_will_ai (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    thread_id UUID NOT NULL,
