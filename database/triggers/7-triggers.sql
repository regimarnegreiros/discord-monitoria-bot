CREATE OR REPLACE FUNCTION question_data_update() RETURNS TRIGGER AS $$
DECLARE
    tag_solved      BIGINT := 1281071345991684238;
    rec             RECORD;
BEGIN
    IF (TG_OP = 'INSERT' AND TG_TABLE_NAME = 'tag_thread') THEN
        IF (NEW.tagID = tag_solved) THEN
            FOR rec IN SELECT t2.subjectID FROM tag_thread t1
                            LEFT JOIN tags t2 ON t1.tagID = t2.tagID
                        WHERE t1.threadID = NEW.threadID
            LOOP
                UPDATE subjects
                    SET questions_data.solved = (questions_data).solved + 1
                WHERE subjects.subjectID = rec.subjectID;
            END LOOP;
            FOR rec IN SELECT t2.discID FROM user_thread t1
                            LEFT JOIN users t2 ON t1.discID = t2.discID
                        WHERE t1.threadID = NEW.threadID
            LOOP
                UPDATE users
                    SET questions_data.solved = (questions_data).solved + 1
                WHERE users.discID = rec.discID;
            END LOOP;
        ELSE
            SELECT subjectID INTO rec FROM tags WHERE NEW.tagID = tags.tagID;
            UPDATE subjects
                    SET questions_data.total = (questions_data).total + 1
            WHERE subjects.subjectID = rec.subjectID;
        END IF;
    ELSIF (TG_OP = 'DELETE' AND TG_TABLE_NAME = 'tag_thread') THEN
        IF (OLD.tagID <> tag_solved) THEN
            UPDATE subjects
                SET questions_data.solved =
                    GREATEST((questions_data).solved - 1, 0),
                questions_data.answered =
                    GREATEST((questions_data).answered - 1, 0),
                questions_data.total =
                    GREATEST((questions_data).total - 1, 0)
            WHERE subjects.subjectID = (SELECT tags.subjectID FROM tags
                                        WHERE tags.tagID = OLD.tagID);
        ELSE
            FOR rec IN SELECT t2.subjectID FROM tag_thread t1
                            LEFT JOIN tags t2 ON t1.tagID = t2.tagID
                        WHERE t1.threadID = OLD.threadID
            LOOP
                UPDATE subjects
                    SET questions_data.solved =
                        GREATEST((questions_data).solved - 1, 0),
                    questions_data.answered = 
                        GREATEST((questions_data).answered - 1, 0),
                    questions_data.total =
                        GREATEST((questions_data).total - 1, 0)
                WHERE subjects.subjectID = rec.subjectID;
            END LOOP;
            FOR rec IN SELECT t2.discID FROM user_thread t1
                            LEFT JOIN users t2 ON t1.discID = t2.discID
                        WHERE t1.threadID = NEW.threadID
            LOOP
                UPDATE users SET questions_data.solved =
                    GREATEST((questions_data).solved - 1, 0)
                WHERE users.discID = rec.threadID;
            END LOOP;
        END IF;
    ELSIF (TG_OP = 'DELETE' AND TG_TABLE_NAME = 'thread') THEN
        UPDATE users
            SET questions_data.solved =
                GREATEST((users.questions_data).solved - 1, 0),
            questions_data.answered =
                GREATEST((users.questions_data).answered - 1, 0),
            questions_data.total =
                GREATEST((users.questions_data).total - 1, 0)
        FROM (SELECT ut.threadID, u.discID, u.questions_data
              FROM users u JOIN user_thread ut ON u.discID = ut.discID
        WHERE ut.threadID = OLD.threadID);
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT' AND TG_TABLE_NAME = 'thread') THEN
        UPDATE users
            SET questions_data.total = (users.questions_data).total + 1
        FROM (SELECT ut.threadID, u.discID, u.questions_data
              FROM users u JOIN user_thread ut ON u.discID = ut.discID) AS uot
        WHERE uot.threadID = NEW.threadID;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER question_data_update_tags
AFTER INSERT OR DELETE ON tag_thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();

CREATE OR REPLACE TRIGGER question_data_update_user_insert
AFTER INSERT ON thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();

CREATE OR REPLACE TRIGGER question_data_update_user_delete
BEFORE DELETE ON thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();

CREATE OR REPLACE FUNCTION user_thread_init() RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO user_thread (discID, threadID)
        VALUES (NEW.threadCreatorID, NEW.threadID);
    ELSE
        DELETE FROM user_thread
        WHERE threadID = OLD.threadID;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER user_thread_init
AFTER INSERT OR DELETE ON thread
FOR EACH ROW EXECUTE FUNCTION user_thread_init();

CREATE OR REPLACE FUNCTION monitors_update() RETURNS TRIGGER AS $$
DECLARE
    current    RECORD;
BEGIN
    SELECT
        floor(EXTRACT(MONTH FROM CURRENT_TIMESTAMP) / 7) + 1
        AS semester,
        EXTRACT(YEAR FROM CURRENT_TIMESTAMP) AS year
    INTO current;

    IF ((TG_OP = 'INSERT' AND NEW.is_monitor = TRUE)
        OR (TG_OP = 'UPDATE' AND OLD.is_monitor = FALSE
                             AND NEW.is_monitor = TRUE)) THEN
        UPDATE semester
            SET monitors = array_append(monitors, NEW.discID)
        WHERE semester = current.semester
          AND semester_year = current.year;
    ELSIF (TG_OP = 'UPDATE' AND OLD.is_monitor = TRUE
                            AND NEW.is_monitor = FALSE) THEN
        UPDATE semester
            SET monitors = array_remove(monitors, OLD.discID)
        WHERE semester = current.semester
          AND semester_year = current.year;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER monitors_update
AFTER INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION monitors_update();

CREATE OR REPLACE FUNCTION semester_dump() RETURNS TRIGGER AS $$
DECLARE
    previous    RECORD;
BEGIN
    SELECT sem.semester, sem.semester_year, sem.monitors INTO previous
    FROM semester sem
    WHERE sem.semester = 3 - NEW.semester
    AND sem.semester_year = NEW.semester_year - (NEW.semester % 2);

    UPDATE semester sem SET monitors = previous.monitors
    WHERE sem.semester = NEW.semester
    AND sem.semester_year = NEW.semester_year;

    /* salva dados de duvida como JSON, ignora materias sem duvida */
    UPDATE semester SET subject_data = sub.jdata FROM (
        SELECT jsonb_agg(jsonb_build_object(
            'subject_id', subjectid,
            'name', subject_name,
            'data', questions_data
        )) AS jdata FROM subjects WHERE questions_data <> (0,0,0)) AS sub
    WHERE semester = previous.semester
    AND semester_year = previous.semester_year;

    /* reset dos dados para novo semestre */
    UPDATE subjects SET questions_data = (0,0,0);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER semester_dump
AFTER INSERT ON semester
FOR EACH ROW EXECUTE FUNCTION semester_dump();
