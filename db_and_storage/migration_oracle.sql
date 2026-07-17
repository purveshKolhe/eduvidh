-- ============================================================================
-- ORACLE DATABASE MIGRATION
-- ============================================================================

CREATE TABLE videos (
    id VARCHAR2(36) PRIMARY KEY,
    prompt CLOB NOT NULL,
    status VARCHAR2(50) DEFAULT 'pending' NOT NULL,
    slides_data CLOB,
    error_message CLOB,
    cold_start_time NUMBER(10, 3),
    rendering_time NUMBER(10, 3),
    video_length NUMBER(10, 3),
    resources_used CLOB,
    video_storage_url VARCHAR2(2048),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index creation timestamp for quick querying
CREATE INDEX idx_videos_created_at ON videos(created_at);

-- Trigger to update updated_at automatically on row updates
CREATE OR REPLACE TRIGGER trg_videos_updated_at
BEFORE UPDATE ON videos
FOR EACH ROW
BEGIN
    :NEW.updated_at := CURRENT_TIMESTAMP;
END;
/
