CREATE OR REPLACE FUNCTION question_data_update() RETURNS TRIGGER AS $$
DECLARE
    tag_solved      BIGINT := 1281071345991684238;
    rec             RECORD;
BEGIN
    /* operacoes diretamente em tag_thread */
    IF (TG_OP = 'INSERT' AND TG_TABLE_NAME = 'tag_thread') THEN
        IF (NEW.tagID = tag_solved) THEN
            /* incrementa solved em materias se a tag foi aplicada */
            FOR rec IN (SELECT t2.subjectID FROM tag_thread t1
                        LEFT JOIN tags t2 ON t1.tagID = t2.tagID
                        WHERE t1.threadID = NEW.threadID)
            LOOP
                UPDATE subjects
                SET questions_data.solved = (questions_data).solved + 1
                WHERE subjects.subjectID = rec.subjectID;
            END LOOP;

            /* incrementa solved em usuarios */
            FOR rec IN (SELECT t2.discID FROM user_thread t1
                        LEFT JOIN users t2 ON t1.discID = t2.discID
                        WHERE t1.threadID = NEW.threadID)
            LOOP
                /* em questions_data para todos os participantes */
                UPDATE users
                SET questions_data.solved = (questions_data).solved + 1
                WHERE users.discID = rec.discID;

                /* e em monitor_data p/ monitores */
                /* (exceto se criou a thread, pois nao agiu como monitor) */
                UPDATE users
                SET monitor_data.solved = (monitor_data).solved + 1
                WHERE users.discID = rec.discID AND is_monitor = TRUE
                AND rec.discID <> (SELECT threadCreatorID FROM thread t
                                   WHERE t.threadID = NEW.threadID);
            END LOOP;
        ELSE
            /* incrementa total de duvidas em cada materia */
            SELECT subjectID INTO rec FROM tags WHERE NEW.tagID = tags.tagID;

            UPDATE subjects
            SET questions_data.total = (questions_data).total + 1
            WHERE subjects.subjectID = rec.subjectID;
        END IF;

    ELSIF (TG_OP = 'DELETE' AND TG_TABLE_NAME = 'tag_thread') THEN
        IF (OLD.tagID <> tag_solved) THEN
            /* decrementa dados de duvidas em materias */
            /* se nao foi a tag de resolvido que foi retirada */
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
            /* decrementa solved se a tag de resolvido foi retirada */
            FOR rec IN (SELECT t2.subjectID FROM tag_thread t1
                        LEFT JOIN tags t2 ON t1.tagID = t2.tagID
                        WHERE t1.threadID = OLD.threadID)
            LOOP
                UPDATE subjects
                SET questions_data.solved =
                    GREATEST((questions_data).solved - 1, 0)
                WHERE subjects.subjectID = rec.subjectID;
            END LOOP;

            FOR rec IN (SELECT t2.discID FROM user_thread t1
                        LEFT JOIN users t2 ON t1.discID = t2.discID
                        WHERE t1.threadID = NEW.threadID)
            LOOP
                /* em usuarios participantes tambem */
                UPDATE users
                SET questions_data.solved =
                    GREATEST((questions_data).solved - 1, 0)
                WHERE users.discID = rec.discID;

                UPDATE users
                SET monitor_data.solved =
                    GREATEST((monitor_data).solved - 1, 0)
                WHERE users.discID = rec.discID AND is_monitor = TRUE
                AND rec.discID <> (SELECT threadCreatorID FROM thread t
                                   WHERE t.threadID = NEW.threadID);
            END LOOP;
        END IF;
    /*ELSIF (TG_OP = 'INSERT' AND TG_TABLE_NAME = 'thread') THEN
        UPDATE users
            SET questions_data.total = (users.questions_data).total + 1
        FROM (SELECT ut.threadID, u.discID, u.questions_data
              FROM users u JOIN user_thread ut ON u.discID = ut.discID) AS uot
        WHERE uot.threadID = NEW.threadID;*/
    ELSIF (TG_OP = 'INSERT' AND TG_TABLE_NAME = 'user_thread') THEN
        /* caso usuario tenha entrado depois em duvida resolvida */
        IF tag_solved IN (SELECT tagID FROM tag_thread tt
                          WHERE tt.threadID = NEW.threadID) THEN
            SELECT threadCreatorID INTO rec
            FROM thread WHERE threadID = NEW.threadID;

            UPDATE users
            SET questions_data.solved = (questions_data).solved + 1
            WHERE users.discID = NEW.discID
            AND NEW.discID <> rec.threadCreatorID;

            UPDATE users
            SET monitor_data.solved = (monitor_data).solved + 1
            WHERE users.discID = NEW.discID AND is_monitor = TRUE
            AND NEW.discID <> rec.threadCreatorID; 
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER question_data_update_tags
AFTER INSERT OR DELETE ON tag_thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();

/*CREATE OR REPLACE TRIGGER question_data_update_user_insert
AFTER INSERT ON thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();*/

CREATE OR REPLACE TRIGGER question_data_update_user_thread_insert
AFTER INSERT ON user_thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();

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

/*
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
*/

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
