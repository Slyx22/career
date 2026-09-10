-- Feature interest tracking table
-- Stores which features users are interested in to help prioritize development

CREATE TABLE IF NOT EXISTS feature_interest (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id TEXT NOT NULL,
  feature_key TEXT NOT NULL,
  user_email TEXT,
  clerk_user_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(analysis_id, feature_key)
);

-- Index for querying popular features
CREATE INDEX idx_feature_interest_key ON feature_interest(feature_key);
CREATE INDEX idx_feature_interest_created ON feature_interest(created_at DESC);

-- RLS policies
ALTER TABLE feature_interest ENABLE ROW LEVEL SECURITY;

-- Allow anyone to insert their interest (they can only see their own)
CREATE POLICY "Users can express interest in features"
  ON feature_interest
  FOR INSERT
  WITH CHECK (true);

-- Users can see their own feature interests
CREATE POLICY "Users can view their own interests"
  ON feature_interest
  FOR SELECT
  USING (
    clerk_user_id = auth.uid()::text
    OR user_email = current_setting('request.jwt.claims', true)::json->>'email'
  );

COMMENT ON TABLE feature_interest IS 'Tracks which upcoming features users are interested in';
COMMENT ON COLUMN feature_interest.feature_key IS 'Unique identifier for the feature (e.g. personalized_roadmap, employer_insights)';
