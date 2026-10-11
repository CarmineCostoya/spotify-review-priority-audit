CREATE TABLE IF NOT EXISTS metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
  review_id TEXT PRIMARY KEY,
  review_text TEXT NOT NULL,
  topic TEXT NOT NULL,
  intent TEXT NOT NULL,
  severity INTEGER NOT NULL,
  evidence_quote TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS issue_membership (
  issue_id TEXT NOT NULL,
  review_id TEXT NOT NULL,
  PRIMARY KEY (issue_id, review_id)
);

CREATE TABLE IF NOT EXISTS ranking (
  rank INTEGER PRIMARY KEY,
  issue_id TEXT UNIQUE NOT NULL,
  complaint_count INTEGER NOT NULL,
  severity_sum INTEGER NOT NULL,
  mean_severity REAL NOT NULL,
  priority_score INTEGER NOT NULL
);
