CREATE TABLE IF NOT EXISTS checkpoints (
    tenant TEXT NOT NULL,
    task TEXT NOT NULL,
    version INTEGER NOT NULL,
    payload TEXT NOT NULL,
    PRIMARY KEY (tenant, task)
);
