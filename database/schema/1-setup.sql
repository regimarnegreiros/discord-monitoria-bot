/* PostgreSQL
 1o a ser executado */

CREATE TYPE STATS_QUESTIONS AS (
    total INT,
    answered INT,
    solved INT
);

CREATE TYPE MONITOR_STATS AS (
    answered INT,
    solved INT
);

CREATE OR REPLACE FUNCTION stats_questions_check(questions_data STATS_QUESTIONS)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (questions_data.total >= 0) AND
           (questions_data.answered >= 0) AND 
           /* (questions_data.answered >= questions_data.solved) AND */
           (questions_data.solved >= 0);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION monitor_data_check(monitor_data MONITOR_STATS)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (monitor_data.answered >= monitor_data.solved) AND
           (monitor_data.solved >= 0);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE
update_users_subjects(thread_id BIGINT) AS $$
DECLARE
    current_semester INT := (SELECT MAX(semesterID) FROM semester);
BEGIN
    /* FALSE = is_answered, TRUE = is_solved */
    WITH subject_counts AS (
        SELECT tags.subjectID, COUNT(*) AS count
        FROM tag_thread tt
        JOIN tags ON tt.tagID = tags.tagID
        LEFT JOIN thread t ON t.threadID = tt.threadID
        WHERE t.is_solved
        AND t.semesterID = current_semester
        GROUP BY tags.subjectID
    )
    UPDATE subjects sub
    SET questions_data.solved = sc.count
    FROM subject_counts sc
    WHERE sub.subjectID = sc.subjectID;

    WITH user_counts AS (
        SELECT ut.discID, COUNT(*) AS count
        FROM user_thread ut
        LEFT JOIN thread t ON t.threadID = ut.threadID
        WHERE t.is_solved
        AND t.semesterID = current_semester
        GROUP BY ut.discID
    )
    UPDATE users
    SET questions_data.solved = uc.count
    FROM user_counts uc
    WHERE users.discID = uc.discID;

    WITH user_counts AS (
        SELECT ut.discID, COUNT(*) AS count
        FROM user_thread ut
        LEFT JOIN thread t ON t.threadID = ut.threadID
        WHERE t.is_solved
        AND t.semesterID = current_semester
        GROUP BY ut.discID
    )
    UPDATE users
    SET monitor_data.solved = uc.count
    FROM user_counts uc
    WHERE users.discID = uc.discID
    AND users.is_monitor
    AND users.discID <> (SELECT threadCreatorID FROM thread
                         WHERE threadID = thread_id);

    WITH subject_counts AS (
        SELECT tags.subjectID, COUNT(*) AS count
        FROM tag_thread tt
        JOIN tags ON tt.tagID = tags.tagID
        LEFT JOIN thread t ON t.threadID = tt.threadID
        WHERE t.is_answered
        AND t.semesterID = current_semester
        GROUP BY tags.subjectID
    )
    UPDATE subjects sub
    SET questions_data.answered = sc.count
    FROM subject_counts sc
    WHERE sub.subjectID = sc.subjectID;

    WITH user_counts AS (
        SELECT ut.discID, COUNT(*) AS count
        FROM user_thread ut
        LEFT JOIN thread t ON t.threadID = ut.threadID
        WHERE t.is_answered
        AND t.semesterID = current_semester
        GROUP BY ut.discID
    )
    UPDATE users
    SET questions_data.answered = uc.count
    FROM user_counts uc
    WHERE users.discID = uc.discID;

    WITH user_counts AS (
        SELECT ut.discID, COUNT(*) AS count
        FROM user_thread ut
        LEFT JOIN thread t ON t.threadID = ut.threadID
        WHERE t.is_solved
        AND t.semesterID = current_semester
        GROUP BY ut.discID
    )
    UPDATE users
    SET monitor_data.answered = uc.count
    FROM user_counts uc
    WHERE users.discID = uc.discID
    AND users.is_monitor
    AND users.discID <> (SELECT threadCreatorID FROM thread
                         WHERE threadID = thread_id);

    WITH subject_counts AS (
        SELECT tags.subjectID, COUNT(*) count FROM tag_thread tt
        LEFT JOIN tags ON tags.tagID = tt.tagID
        LEFT JOIN thread t ON tt.threadID = t.threadID
        WHERE t.semesterID = current_semester
        GROUP BY tags.subjectID
    )
    UPDATE subjects sub
    SET questions_data.total = sc.count
    FROM subject_counts sc
    WHERE sub.subjectID = sc.subjectID;

    WITH user_counts AS (
        SELECT users.discID, COUNT(*) count FROM user_thread ut
        LEFT JOIN users ON users.discID = ut.discID
        LEFT JOIN thread t ON ut.threadID = t.threadID
        WHERE t.semesterID = current_semester
        GROUP BY users.discID
    )
    UPDATE users
    SET questions_data.total = uc.count
    FROM user_counts uc
    WHERE users.discID = uc.discID;

END;
$$ LANGUAGE plpgsql;

/*SET client_min_messages TO WARNING;*/
