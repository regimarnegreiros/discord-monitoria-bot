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
    WITH subject_counts_solved AS (
        SELECT sub.subjectID, COUNT(t.*) AS count
        FROM subjects sub
        LEFT JOIN tags ON tags.subjectID = sub.subjectID
        LEFT JOIN tag_thread tt ON tt.tagID = tags.tagID
        LEFT JOIN thread t ON t.threadID = tt.threadID
        WHERE t.is_solved AND t.semesterID = current_semester
        GROUP BY sub.subjectID
    ),
    subject_counts_answered AS (
        SELECT sub.subjectID, COUNT(t.*) AS count
        FROM subjects sub
        LEFT JOIN tags ON tags.subjectID = sub.subjectID
        LEFT JOIN tag_thread tt ON tt.tagID = tags.tagID
        LEFT JOIN thread t ON t.threadID = tt.threadID
        WHERE t.is_answered AND t.semesterID = current_semester
        GROUP BY sub.subjectID
    ),
    subject_counts_total AS (
        SELECT sub.subjectID, COUNT(t.*) AS count
        FROM subjects sub
        LEFT JOIN tags ON tags.subjectID = sub.subjectID
        LEFT JOIN tag_thread tt ON tt.tagID = tags.tagID
        LEFT JOIN thread t ON t.threadID = tt.threadID
        WHERE t.semesterID = current_semester
        GROUP BY sub.subjectID
    ),
    all_subjects AS (
        SELECT subjectID FROM subject_counts_total
        UNION
        SELECT subjectID FROM subject_counts_answered
        UNION
        SELECT subjectID FROM subject_counts_solved
    )
    UPDATE subjects sub
    SET questions_data = (
        COALESCE(sct.count, 0),
        COALESCE(sca.count, 0),
        COALESCE(scs.count, 0)
    )
    FROM all_subjects a
    LEFT JOIN subject_counts_total sct ON sct.subjectID = a.subjectID
    LEFT JOIN subject_counts_answered sca ON sca.subjectID = a.subjectID
    LEFT JOIN subject_counts_solved scs ON scs.subjectID = a.subjectID
    WHERE sub.subjectID = a.subjectID;

    WITH user_counts_solved AS (
        SELECT ut.discID, COUNT(*) AS count
        FROM user_thread ut
        LEFT JOIN thread t ON t.threadID = ut.threadID
        WHERE t.is_solved
        AND t.semesterID = current_semester
        GROUP BY ut.discID
    ),
    user_counts_answered AS (
        SELECT ut.discID, COUNT(*) AS count
        FROM user_thread ut
        LEFT JOIN thread t ON t.threadID = ut.threadID
        WHERE t.is_answered
        AND t.semesterID = current_semester
        GROUP BY ut.discID
    ),
    user_counts_total AS (
        SELECT users.discID, COUNT(*) count FROM user_thread ut
        LEFT JOIN users ON users.discID = ut.discID
        LEFT JOIN thread t ON ut.threadID = t.threadID
        WHERE t.semesterID = current_semester
        GROUP BY users.discID
    )
    UPDATE users
    SET questions_data = (uct.count, uca.count, ucs.count)
    FROM user_counts_solved ucs
        JOIN user_counts_answered uca
        ON uca.discID = ucs.discID
        JOIN user_counts_total uct
        ON uct.discID = ucs.discID
    WHERE users.discID = ucs.discID;

    WITH user_counts_solved AS (
        SELECT ut.discID, COUNT(*) AS count
        FROM user_thread ut
        LEFT JOIN thread t ON t.threadID = ut.threadID
        WHERE t.is_solved
        AND t.semesterID = current_semester
        GROUP BY ut.discID
    ),
    user_counts_answered AS (
        SELECT ut.discID, COUNT(*) AS count
        FROM user_thread ut
        LEFT JOIN thread t ON t.threadID = ut.threadID
        WHERE t.is_answered
        AND t.semesterID = current_semester
        GROUP BY ut.discID
    ),
    user_counts_total AS (
        SELECT users.discID, COUNT(*) count FROM user_thread ut
        LEFT JOIN users ON users.discID = ut.discID
        LEFT JOIN thread t ON ut.threadID = t.threadID
        WHERE t.semesterID = current_semester
        GROUP BY users.discID
    )
    UPDATE users
    SET questions_data = (uct.count, uca.count, ucs.count)
    FROM user_counts_solved ucs
        JOIN user_counts_answered uca
        ON uca.discID = ucs.discID
        JOIN user_counts_total uct
        ON uct.discID = ucs.discID
    WHERE users.discID = ucs.discID
    AND users.is_monitor
    AND users.discID <> (SELECT threadCreatorID FROM thread
                         WHERE threadID = thread_id);

END;
$$ LANGUAGE plpgsql;

/*SET client_min_messages TO WARNING;*/
