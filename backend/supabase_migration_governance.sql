-- Governance Checkpoints Table Migration
-- Adds governance verification tracking for agent operations

CREATE TABLE IF NOT EXISTS governance_checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    action TEXT NOT NULL, -- 'deployment', 'purchase', 'rental', 'certification', 'autonomous_execution'
    agent_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    state JSONB NOT NULL, -- Current system state at checkpoint
    metrics JSONB NOT NULL, -- Metrics used for verification
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    drift_score REAL NOT NULL DEFAULT 0.0
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_governance_checkpoints_agent ON governance_checkpoints(agent_id);
CREATE INDEX IF NOT EXISTS idx_governance_checkpoints_user ON governance_checkpoints(user_id);
CREATE INDEX IF NOT EXISTS idx_governance_checkpoints_action ON governance_checkpoints(action);
CREATE INDEX IF NOT EXISTS idx_governance_checkpoints_timestamp ON governance_checkpoints(timestamp);
CREATE INDEX IF NOT EXISTS idx_governance_checkpoints_verified ON governance_checkpoints(verified);

-- User profiles table extension for governance metrics
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS trust_score REAL DEFAULT 50.0,
ADD COLUMN IF NOT EXISTS governance_flags JSONB DEFAULT '{}';

-- Agent purchases table for tracking governed transactions
CREATE TABLE IF NOT EXISTS agent_purchases (
    id SERIAL PRIMARY KEY,
    agent_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    transaction_id TEXT UNIQUE NOT NULL,
    purchase_type TEXT NOT NULL, -- 'purchase', 'rental'
    amount REAL,
    duration_hours INTEGER, -- For rentals
    status TEXT NOT NULL DEFAULT 'completed',
    governance_checkpoint TEXT REFERENCES governance_checkpoints(checkpoint_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for agent purchases
CREATE INDEX IF NOT EXISTS idx_agent_purchases_agent ON agent_purchases(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_purchases_user ON agent_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_purchases_transaction ON agent_purchases(transaction_id);

-- Agent deployments table for tracking governed deployments
CREATE TABLE IF NOT EXISTS agent_deployments (
    id SERIAL PRIMARY KEY,
    agent_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    deployment_id TEXT UNIQUE NOT NULL,
    deployment_config JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    governance_checkpoint TEXT REFERENCES governance_checkpoints(checkpoint_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for agent deployments
CREATE INDEX IF NOT EXISTS idx_agent_deployments_agent ON agent_deployments(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_deployments_user ON agent_deployments(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_deployments_deployment ON agent_deployments(deployment_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for agent_deployments
CREATE TRIGGER update_agent_deployments_updated_at
    BEFORE UPDATE ON agent_deployments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();