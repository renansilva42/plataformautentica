-- SQL command to create messages table in Supabase
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    thread_id UUID NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'ai')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Index for faster queries by thread_id and created_at
CREATE INDEX IF NOT EXISTS idx_messages_thread_created_at ON messages(thread_id, created_at);
