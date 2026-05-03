-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table to manage video generation state
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- States: pending, script_generated, audio_generated, rendering, completed, failed
    slides_data JSONB, -- Will store the generated script and TTS audio durations for each slide
    video_url TEXT, -- Final output URL (if uploading to Supabase Storage)
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optional: Create a storage bucket for outputs and audio temp files
-- Requires storage privileges; if it fails, you can create the bucket manually via the Supabase UI.
INSERT INTO storage.buckets (id, name, public) VALUES ('video-assets', 'video-assets', true);
