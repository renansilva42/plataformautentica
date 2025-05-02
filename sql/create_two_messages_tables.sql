-- SQL command to create messages table for Capivara Analista
CREATE TABLE IF NOT EXISTS messages_analista (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    thread_id UUID NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'ai')),
    content TEXT NOT NULL,
    nome TEXT,
    instagram TEXT,
    telefone TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_messages_analista_thread_created_at ON messages_analista(thread_id, created_at);

-- SQL command to create messages table for Capivara do Conteúdo
CREATE TABLE IF NOT EXISTS messages_conteudo (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    thread_id UUID NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'ai')),
    content TEXT NOT NULL,
    nome TEXT,
    instagram TEXT,
    telefone TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_messages_conteudo_thread_created_at ON messages_conteudo(thread_id, created_at);
