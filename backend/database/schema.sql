CREATE TABLE IF NOT EXISTS analysis_records (
    id TEXT PRIMARY KEY,
    agent TEXT NOT NULL,
    modality TEXT NOT NULL,
    input_payload JSON NOT NULL,
    output_payload JSON,
    risk_score REAL NOT NULL DEFAULT 0.0,
    decision TEXT NOT NULL,
    explanation TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS moderation_actions (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    action TEXT NOT NULL,
    rationale TEXT NOT NULL,
    reviewer_group TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_moderation_actions_analysis_id
    ON moderation_actions (analysis_id);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    action TEXT,
    actor_id TEXT,
    actor_role TEXT,
    resource_type TEXT,
    resource_id TEXT,
    request_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    payload JSON NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_accounts (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    key_prefix TEXT NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    scopes JSON NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    revoked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_accounts (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS feedback_records (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    submitted_by_user_id TEXT,
    label TEXT NOT NULL,
    comment TEXT,
    confidence_rating REAL,
    is_actionable INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL,
    active_learning_bucket TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submitted_by_user_id) REFERENCES user_accounts (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS retraining_jobs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    triggered_by_user_id TEXT,
    dataset_path TEXT,
    model_version TEXT,
    source_window_days INTEGER NOT NULL DEFAULT 30,
    source_snapshot JSON NOT NULL,
    notes TEXT,
    metrics JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (triggered_by_user_id) REFERENCES user_accounts (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS usage_metrics (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    principal_id TEXT,
    principal_role TEXT,
    route TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    duration_ms INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notification_logs (
    id TEXT PRIMARY KEY,
    recipient TEXT,
    channel TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    delivery_status TEXT NOT NULL,
    delivery_error TEXT,
    details JSON NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP
);
