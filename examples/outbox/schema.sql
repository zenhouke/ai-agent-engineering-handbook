CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    tenant TEXT NOT NULL,
    payload TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    approved_hash TEXT NOT NULL,
    approved_until INTEGER NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('approved', 'queued', 'executing', 'confirmed')),
    version INTEGER NOT NULL
);
CREATE TABLE outbox (
    operation_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL UNIQUE REFERENCES tasks(task_id),
    tenant TEXT NOT NULL,
    payload TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('pending', 'unknown', 'confirmed')),
    receipt TEXT
);
