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
            UPDATE users_on_thread ut
                SET questions_data.solved = (questions_data).solved + 1
            WHERE ut.threadID = NEW.threadID;
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
            UPDATE users_on_thread ut
                SET questions_data.solved =
                    GREATEST((questions_data).solved - 1, 0)
            WHERE ut.threadID = OLD.threadID;
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

CREATE OR REPLACE FUNCTION user_monitor() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_monitor = TRUE THEN
        UPDATE semester
            SET monitors = array_append(monitors, NEW.discID)
        WHERE
            semester_year = EXTRACT(YEAR FROM CURRENT_DATE) AND
            semester = CASE WHEN EXTRACT(MONTH FROM CURRENT_DATE) <= 6
                       THEN 1 ELSE 2 END;
    ELSIF (OLD.is_monitor = TRUE AND NEW.is_monitor = FALSE) THEN
        UPDATE semester
            SET monitors = array_remove(monitors, NEW.discID)
        WHERE
            semester_year = EXTRACT(YEAR FROM CURRENT_DATE) AND
            semester = CASE WHEN EXTRACT(MONTH FROM CURRENT_DATE) <= 6
                       THEN 1 ELSE 2 END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER user_monitor
AFTER INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION user_monitor();
