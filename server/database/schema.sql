-- Face Recognition Attendance System - Optimized Database Schema
-- PostgreSQL with pgvector extension

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist
DROP TABLE IF EXISTS attendance_logs CASCADE;
DROP TABLE IF EXISTS face_embeddings CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table - Minimal and optimized
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    student_code VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Face embeddings table - Optimized
CREATE TABLE face_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    embedding VECTOR(128) NOT NULL,
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Attendance logs table - Minimal
CREATE TABLE attendance_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    confidence REAL,
    device_id VARCHAR(50) DEFAULT 'web'
);

-- Indexes for performance
CREATE INDEX idx_users_student_code ON users(student_code);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_face_embeddings_user_id ON face_embeddings(user_id);
CREATE INDEX idx_attendance_logs_user_id ON attendance_logs(user_id);
CREATE INDEX idx_attendance_logs_timestamp ON attendance_logs(timestamp);

-- Vector similarity search index
CREATE INDEX idx_face_embeddings_vector ON face_embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Function for vector similarity search - Optimized
CREATE OR REPLACE FUNCTION find_similar_faces(
    query_embedding VECTOR(128),
    similarity_threshold REAL DEFAULT 0.3,
    max_results INTEGER DEFAULT 3
)
RETURNS TABLE (
    user_id INTEGER,
    name VARCHAR,
    student_code VARCHAR,
    similarity REAL,
    confidence REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.name,
        u.student_code,
        1 - (fe.embedding <=> query_embedding) as similarity,
        fe.confidence
    FROM face_embeddings fe
    JOIN users u ON fe.user_id = u.id
    WHERE u.is_active = TRUE
    AND 1 - (fe.embedding <=> query_embedding) >= similarity_threshold
    ORDER BY fe.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data for testing
INSERT INTO users (name, student_code, department) VALUES
('Nguyễn Văn A', 'SV001', 'CNTT'),
('Trần Thị B', 'SV002', 'CNTT'),
('Lê Văn C', 'SV003', 'CNTT')
ON CONFLICT (student_code) DO NOTHING;

-- Insert sample face embeddings (dummy 128D vectors)
INSERT INTO face_embeddings (user_id, embedding, confidence) VALUES
(1, array_fill(0.1, ARRAY[128]), 0.95),
(2, array_fill(0.2, ARRAY[128]), 0.92),
(3, array_fill(0.3, ARRAY[128]), 0.88)
ON CONFLICT DO NOTHING;
