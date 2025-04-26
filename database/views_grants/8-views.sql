CREATE VIEW IF NOT EXISTS monitors AS
SELECT discID, monitor_data FROM users
WHERE is_monitor = TRUE;
