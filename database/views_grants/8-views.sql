CREATE VIEW monitors AS
SELECT discID, monitor_data FROM users
WHERE is_monitor = TRUE;
