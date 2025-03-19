-- 3o a ser executado

CREATE TABLE IF NOT EXISTS comp_user_thread (
    mapID SERIAL PRIMARY KEY,
    discID BIGINT REFERENCES comp_user(discID) ON UPDATE CASCADE ON DELETE CASCADE,
    threadID BIGINT REFERENCES thread(threadID) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tag_thread (
    mapID SERIAL PRIMARY KEY,
    threadID BIGINT NOT NULL REFERENCES thread(threadID) ON DELETE CASCADE,
    tagID BIGINT REFERENCES tags(tagID),
    CONSTRAINT unique_tags UNIQUE (threadID, tagID)
);

CREATE TABLE IF NOT EXISTS semester_subject (
    mapID SERIAL PRIMARY KEY,
    semesterID BIGINT NOT NULL REFERENCES semester(semesterID),
    subjectID VARCHAR(7) NOT NULL REFERENCES comp_subject(subjectID),
    stats_subject_semester STATS_QUESTIONS NOT NULL,
    monitorIDs BIGINT[],
    CHECK (stats_questions_check(stats_subject_semester))
);
-- 20241, mdc119, (15, 10, 8)