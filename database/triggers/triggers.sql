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
                UPDATE comp_subject
                    SET questions_data.solved = (questions_data).solved + 1
                WHERE comp_subject.subjectID = rec.subjectID;
            END LOOP;
        ELSE
            SELECT subjectID INTO rec FROM tags WHERE NEW.tagID = tags.tagID;
            UPDATE comp_subject
                    SET questions_data.total = (questions_data).total + 1
            WHERE comp_subject.subjectID = rec.subjectID;
        END IF;
    ELSE
        IF (OLD.tagID <> tag_solved) THEN
            SELECT tags.subjectID INTO rec
            FROM tags WHERE tags.tagID = OLD.tagID;

            UPDATE comp_subject
                SET questions_data.solved = (questions_data).solved - 1
            WHERE comp_subject.subjectID = rec.subjectID;
            UPDATE comp_subject
                SET questions_data.answered = (questions_data).answered - 1
            WHERE comp_subject.subjectID = rec.subjectID;
            UPDATE comp_subject
                SET questions_data.total = (questions_data).total - 1
            WHERE comp_subject.subjectID = rec.subjectID;
        ELSE
            FOR rec IN SELECT t2.subjectID FROM tag_thread t1
                            LEFT JOIN tags t2 ON t1.tagID = t2.tagID
                        WHERE t1.threadID = OLD.threadID
            LOOP
                UPDATE comp_subject
                    SET questions_data.solved = (questions_data).solved - 1
                WHERE comp_subject.subjectID = rec.subjectID;
                UPDATE comp_subject
                    SET questions_data.answered = (questions_data).answered - 1
                WHERE comp_subject.subjectID = rec.subjectID;
                UPDATE comp_subject
                    SET questions_data.total = (questions_data).total - 1
                WHERE comp_subject.subjectID = rec.subjectID;
            END LOOP;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER question_data_update
AFTER INSERT OR DELETE ON tag_thread
FOR EACH ROW EXECUTE FUNCTION question_data_update();
