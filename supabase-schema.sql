-- ============================================================
-- Market Intelligence & B2B Lead Scraper - Database Schema
-- Paste this into Supabase Dashboard > SQL Editor
-- ============================================================

-- 1. TRENDS TABLE (Trend Analyzer results)
CREATE TABLE IF NOT EXISTS trends (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    niche TEXT NOT NULL,
    theme TEXT NOT NULL,
    description TEXT,
    source TEXT,                  -- 'reddit', 'twitter', 'ecommerce', 'pinterest'
    source_url TEXT,
    keyword TEXT,
    score DECIMAL(5,2),           -- trend strength 0-100
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries by niche
CREATE INDEX IF NOT EXISTS idx_trends_niche ON trends(niche);
CREATE INDEX IF NOT EXISTS idx_trends_created ON trends(created_at DESC);

-- 2. LEADS TABLE (Lead Generator results)
CREATE TABLE IF NOT EXISTS leads (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    business_name TEXT NOT NULL,
    category TEXT,
    address TEXT,
    phone TEXT,
    website TEXT,
    google_rating DECIMAL(3,1),
    has_website BOOLEAN DEFAULT FALSE,
    website_quality TEXT,         -- 'none', 'poor', 'decent', 'good'
    needs_improvement BOOLEAN DEFAULT TRUE,
    pitch_angle TEXT,             -- AI-generated pitch suggestion
    lead_score INT DEFAULT 0,     -- 0-100
    source TEXT,                  -- 'google_maps', 'directory', etc.
    location TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for filtering
CREATE INDEX IF NOT EXISTS idx_leads_category ON leads(category);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(lead_score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_website ON leads(has_website);

-- Enable Row Level Security (optional for now, but good practice)
ALTER TABLE trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Allow public read/write for development (tighten later)
CREATE POLICY "Allow all on trends" ON trends
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all on leads" ON leads
    FOR ALL USING (true) WITH CHECK (true);
