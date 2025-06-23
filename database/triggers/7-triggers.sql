CREATE OR REPLACE FUNCTION question_data_update() RETURNS TRIGGER AS $$
DECLARE
    tag_solved      BIGINT := 1281071345991684238;
    current_semester INT := (SELECT MAX(semesterID) FROM semester);
    rec             RECORD;
BEGIN
    /* operacoes diretamente em tag_thread */
    IF (TG_OP = 'INSERT' AND TG_TABLE_NAME = 'tag_thread') THEN
        IF (NEW.tagID = tag_solved) THEN
            /* incrementa solved em materias se a tag foi aplicada */
            UPDATE thread t SET is_solved = TRUE
            WHERE t.threadID = NEW.threadID;
            /* implementar trigger de setar solved como count */
        ELSE
            /* seta total de duvidas em cada materia */
            SELECT tags.subjectID, COUNT(*) count INTO rec
            FROM tags JOIN tag_thread tt ON tags.tagID = tt.tagID
            LEFT JOIN thread t ON tt.threadID = t.threadID
            WHERE tags.tagID = NEW.tagID
            AND t.semesterID = current_semester
            GROUP BY subjectID;

            UPDATE subjects
            SET questions_data.total = rec.count
            WHERE subjects.subjectID = rec.subjectID;
        END IF;

        CALL update_users_subjects(NEW.threadID);

    ELSIF (TG_OP = 'DELETE' AND TG_TABLE_NAME = 'tag_thread') THEN
        IF (OLD.tagID <> tag_solved) THEN
            /* decrementa dados de duvidas em materias */
            /* se nao foi a tag de resolvido que foi retirada */
            /* SELECT tags.subjectID, COUNT (*) count INTO rec
            FROM tags JOIN tag_thread tt ON tags.tagID = tt.tagID
            LEFT JOIN thread t ON tt.threadID = t.threadID
            WHERE tags.tagID = OLD.tagID
            AND t.semesterID = current_semester
            GROUP BY subjectID;

            UPDATE subjects
            SET questions_data.total = rec.count
            WHERE subjects.subjectID = rec.subjectID; */
            SELECT tags.subjectID INTO rec
            FROM tags
            WHERE tags.tagID = OLD.tagID;

            IF rec.subjectID IS NOT NULL THEN
                UPDATE subjects
                SET questions_data.total = (
                    SELECT COUNT(*) FROM tag_thread tt
                    LEFT JOIN thread t ON tt.threadID = t.threadID
                    WHERE tt.tagID = OLD.tagID
                    AND t.semesterID = current_semester
                ),
                questions_data.answered = (
                    SELECT COUNT(*) FROM tag_thread tt
                    LEFT JOIN thread t ON tt.threadID = t.threadID
                    WHERE tt.tagID = OLD.tagID
                    AND t.is_answered
                    AND t.semesterID = current_semester
                ),
                questions_data.solved = (
                    SELECT COUNT(*) FROM tag_thread tt
                    LEFT JOIN thread t ON tt.threadID = t.threadID
                    WHERE tt.tagID = OLD.tagID
                    AND t.is_solved
                    AND t.semesterID = current_semester
                )
                WHERE subjects.subjectID = rec.subjectID;
            END IF;

        ELSE
            /* decrementa solved se a tag de resolvido foi retirada */
            UPDATE thread t SET is_solved = FALSE
            WHERE t.threadID = OLD.threadID;
        END IF;

        CALL update_users_subjects(OLD.threadID);

        RETURN OLD;

    ELSIF (TG_OP = 'INSERT' AND TG_TABLE_NAME = 'user_thread') THEN
        /* caso usuario tenha entrado depois em duvida resolvida */
        UPDATE users SET
            questions_data.answered = (
                SELECT COUNT(*) FROM user_thread ut LEFT JOIN thread t
                ON t.threadID = ut.threadID WHERE ut.discID = NEW.discID
                AND t.is_answered
                AND t.semesterID = current_semester
            ),
            questions_data.solved = (
                SELECT COUNT(*) FROM user_thread ut LEFT JOIN thread t
                ON t.threadID = ut.threadID WHERE ut.discID = NEW.discID
                AND t.is_solved
                AND t.semesterID = current_semester
            )
        WHERE users.discID = NEW.discID;

        UPDATE users SET
            monitor_data.answered = (
                SELECT COUNT(*) FROM user_thread ut LEFT JOIN thread t
                ON t.threadID = ut.threadID WHERE ut.discID = NEW.discID
                AND t.is_answered
                AND t.semesterID = current_semester
            ),
            monitor_data.solved = (
                SELECT COUNT(*) FROM user_thread ut LEFT JOIN thread t
                ON t.threadID = ut.threadID WHERE ut.discID = NEW.discID
                AND t.is_solved
                AND t.semesterID = current_semester
            )
        WHERE users.discID = NEW.discID AND is_monitor = TRUE
        AND NEW.discID <> (SELECT threadCreatorID FROM thread t
                           WHERE t.threadID = NEW.threadID);

        CALL update_users_subjects(NEW.threadID);

    ELSIF (TG_OP = 'DELETE' AND TG_TABLE_NAME = 'user_thread') THEN
        UPDATE users SET
            questions_data.answered = (
                SELECT COUNT(*) FROM user_thread ut LEFT JOIN thread t
                ON t.threadID = ut.threadID WHERE ut.discID = OLD.discID
                AND t.is_answered
                AND t.semesterID = current_semester
            ),
            questions_data.solved = (
                SELECT COUNT(*) FROM user_thread ut LEFT JOIN thread t
                ON t.threadID = ut.threadID WHERE ut.discID = OLD.discID
                AND t.is_solved
                AND t.semesterID = current_semester
            )
        WHERE users.discID = OLD.discID;

        UPDATE users SET
            monitor_data.answered = (
                SELECT COUNT(*) FROM user_thread ut LEFT JOIN thread t
                ON t.threadID = ut.threadID WHERE ut.discID = OLD.discID
                AND t.is_answered
                AND t.semesterID = current_semester
            ),
            monitor_data.solved = (
                SELECT COUNT(*) FROM user_thread ut LEFT JOIN thread t
                ON t.threadID = ut.threadID WHERE ut.discID = OLD.discID
                AND t.is_solved
                AND t.semesterID = current_semester
            )
        WHERE users.discID = OLD.discID AND is_monitor = TRUE
        AND OLD.discID <> (SELECT threadCreatorID FROM thread t
                           WHERE t.threadID = OLD.threadID);

        WITH user_counts AS (
            SELECT users.discID, COUNT(*) count FROM user_thread ut
            LEFT JOIN users ON users.discID = ut.discID
            LEFT JOIN thread t ON ut.threadID = t.threadID
            WHERE t.semesterID = current_semester
            GROUP BY users.discID
        )
        UPDATE users
        SET questions_data.total = (
            SELECT COUNT(*) FROM user_thread ut LEFT JOIN thread t
            ON t.threadID = ut.threadID WHERE ut.discID = OLD.discID
            AND t.semesterID = current_semester
        )
        FROM user_counts uc
        WHERE users.discID = OLD.discID;

        CALL update_users_subjects(OLD.threadID);

        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER question_data_update_tags_insert
AFTER INSERT ON tag_thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();

CREATE OR REPLACE TRIGGER question_data_update_tags_delete
BEFORE DELETE ON tag_thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();

CREATE OR REPLACE TRIGGER question_data_update_user_thread_insert
AFTER INSERT ON user_thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();

CREATE OR REPLACE TRIGGER question_data_update_user_thread_delete
BEFORE DELETE ON user_thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();

CREATE OR REPLACE FUNCTION answered_solved_update() RETURNS TRIGGER AS $$
DECLARE
    rec         RECORD;
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        CALL update_users_subjects(NEW.threadID);
    ELSE
        UPDATE thread t SET
        is_solved = FALSE, is_answered = FALSE
        WHERE t.threadID = OLD.threadID;

        RETURN OLD;

    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER answered_solved_update
AFTER UPDATE ON thread
FOR EACH ROW
/* WHEN ((OLD.is_solved IS DISTINCT FROM NEW.is_solved)
    OR (OLD.is_answered IS DISTINCT FROM NEW.is_answered)) */
EXECUTE FUNCTION answered_solved_update();

CREATE OR REPLACE TRIGGER answered_solved_delete
AFTER DELETE ON thread
FOR EACH ROW EXECUTE FUNCTION answered_solved_update();

CREATE OR REPLACE FUNCTION user_thread_init() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_thread (discID, threadID)
    VALUES (NEW.threadCreatorID, NEW.threadID);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER user_thread_init
AFTER INSERT ON thread
FOR EACH ROW EXECUTE FUNCTION user_thread_init();

CREATE OR REPLACE FUNCTION semester_dump() RETURNS TRIGGER AS $$
DECLARE
    previous    RECORD;
BEGIN
    SELECT sem.semester, sem.semester_year, sem.user_data INTO previous
    FROM semester sem
    WHERE sem.semester = 3 - NEW.semester
    AND sem.semester_year = NEW.semester_year - (NEW.semester % 2);

    /* salva dados de duvida como JSON, ignora materias sem duvida */
    UPDATE semester SET subject_data = sub.jdata FROM (
        SELECT jsonb_agg(jsonb_build_object(
            'subject_id', subjectid,
            'name', subject_name,
            'questions_data', questions_data
        )) AS jdata FROM subjects WHERE questions_data <> (0,0,0)) AS sub
    WHERE semester = previous.semester
    AND semester_year = previous.semester_year;

    UPDATE semester SET user_data = u.jdata FROM (
        SELECT jsonb_agg(jsonb_build_object(
            'discID', discID,
            'is_monitor', is_monitor,
            'questions_data', questions_data,
            'monitor_data', monitor_data
        )) AS jdata FROM users WHERE (
            (NOT is_monitor AND questions_data <> (0,0,0))
            OR (is_monitor AND monitor_data <> (0,0))
        )) AS u
    WHERE semester = previous.semester
    AND semester_year = previous.semester_year;

    /* reset dos dados para novo semestre */
    UPDATE subjects SET questions_data = (0,0,0);
    UPDATE users SET questions_data = (0,0,0);
    UPDATE users SET monitor_data = (0,0) WHERE monitor_data IS NOT NULL;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER semester_dump
AFTER INSERT ON semester
FOR EACH ROW EXECUTE FUNCTION semester_dump();
