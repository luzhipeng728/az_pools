CREATE TABLE IF NOT EXISTS az_keys (
    id SERIAL PRIMARY KEY,
    resourceName VARCHAR(255) UNIQUE,
    key VARCHAR(255) UNIQUE,
    status VARCHAR(50),
    addTime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_in_use BOOLEAN
);

INSERT INTO az_keys (resourceName, key, status, is_in_use) VALUES
('0232-in', 'cf57bb5538ae4f1a80fadf7a10db92c0', 'suspend', FALSE);