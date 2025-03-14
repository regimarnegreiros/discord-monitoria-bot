-- 3o a ser executado

CREATE TABLE IF NOT EXISTS comp_user_thread (
    mapID SERIAL PRIMARY KEY,
    discID INT REFERENCES comp_user(discID) ON UPDATE CASCADE ON DELETE CASCADE,
    threadID INT REFERENCES thread(threadID) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tag_thread (
    mapID SERIAL PRIMARY KEY,
    tagID INT REFERENCES tags(tagID),
    threadID INT NOT NULL REFERENCES thread(threadID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS semester_subject (
    mapID SERIAL PRIMARY KEY,
    semesterID INT NOT NULL REFERENCES semester(semesterID),
    subjectID INT NOT NULL REFERENCES comp_subject(subjectID),
    stats_subject_semester STATS_QUESTIONS NOT NULL,
    CHECK (stats_questions_check(stats_subject_semester))
);
