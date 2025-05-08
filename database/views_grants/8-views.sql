CREATE VIEW monitors AS
SELECT discID, monitor_data FROM users u
WHERE u.is_monitor;

/* naive: dados semi-incorretos */
CREATE VIEW helpers AS
SELECT discID, questions_data FROM users u
WHERE NOT u.is_monitor
AND (u.questions_data).total < (u.questions_data).answered;
