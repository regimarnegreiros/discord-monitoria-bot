CREATE OR REPLACE FUNCTION question_data_update() RETURNS TRIGGER AS $$
DECLARE
    tag_solved      BIGINT := 1281071345991684238;
    rec             RECORD;
BEGIN
    IF (TG_OP = 'INSERT') THEN
        IF (NEW.tagID = tag_solved) THEN
            FOR rec IN SELECT t2.subjectID FROM tag_thread t1
                            LEFT JOIN tags t2 ON t1.tagID = t2.tagID
                        WHERE t1.threadID = NEW.threadID
            LOOP
                UPDATE subjects
                    SET questions_data.solved = (questions_data).solved + 1
                WHERE subjects.subjectID = rec.subjectID;
            END LOOP;
        ELSE
            SELECT subjectID INTO rec FROM tags WHERE NEW.tagID = tags.tagID;
            UPDATE subjects
                    SET questions_data.total = (questions_data).total + 1
            WHERE subjects.subjectID = rec.subjectID;
        END IF;
    ELSE
        IF (OLD.tagID <> tag_solved) THEN
            SELECT tags.subjectID INTO rec
            FROM tags WHERE tags.tagID = OLD.tagID;

            UPDATE subjects
                SET questions_data.solved = (questions_data).solved - 1
            WHERE subjects.subjectID = rec.subjectID;
            UPDATE subjects
                SET questions_data.answered = (questions_data).answered - 1
            WHERE subjects.subjectID = rec.subjectID;
            UPDATE subjects
                SET questions_data.total = (questions_data).total - 1
            WHERE subjects.subjectID = rec.subjectID;
        ELSE
            FOR rec IN SELECT t2.subjectID FROM tag_thread t1
                            LEFT JOIN tags t2 ON t1.tagID = t2.tagID
                        WHERE t1.threadID = OLD.threadID
            LOOP
                UPDATE subjects
                    SET questions_data.solved = (questions_data).solved - 1
                WHERE subjects.subjectID = rec.subjectID;
                UPDATE subjects
                    SET questions_data.answered = (questions_data).answered - 1
                WHERE subjects.subjectID = rec.subjectID;
                UPDATE subjects
                    SET questions_data.total = (questions_data).total - 1
                WHERE subjects.subjectID = rec.subjectID;
            END LOOP;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER question_data_update
AFTER INSERT OR DELETE ON tag_thread
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
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER user_thread_init
AFTER INSERT OR DELETE ON thread
FOR EACH ROW EXECUTE FUNCTION user_thread_init();
