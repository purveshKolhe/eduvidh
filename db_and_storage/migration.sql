-- ============================================================================
-- POSTGRESQL MIGRATION
-- ============================================================================

-- Enable the UUID extension to generate v4 UUIDs automatically
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    slides_data JSONB,
    error_message TEXT,
    cold_start_time DECIMAL(10, 3),
    rendering_time DECIMAL(10, 3),
    video_length DECIMAL(10, 3),
    resources_used JSONB,
    video_storage_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing creation timestamps
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at);

-- ============================================================================
-- MYSQL MIGRATION (Alternative)
-- ============================================================================
/*
CREATE TABLE IF NOT EXISTS videos (
    id CHAR(36) PRIMARY KEY,
    prompt TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    slides_data JSON,
    error_message TEXT,
    cold_start_time DECIMAL(10, 3),
    rendering_time DECIMAL(10, 3),
    video_length DECIMAL(10, 3),
    resources_used JSON,
    video_storage_url VARCHAR(2048),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Index creation timestamp index
CREATE INDEX idx_videos_created_at ON videos(created_at);
*/
