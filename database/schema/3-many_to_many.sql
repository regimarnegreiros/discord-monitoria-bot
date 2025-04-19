/* 3o a ser executado */

CREATE TABLE IF NOT EXISTS user_thread (
    mapID SERIAL PRIMARY KEY,
    discID BIGINT NOT NULL REFERENCES users(discID) ON DELETE CASCADE,
    threadID BIGINT NOT NULL REFERENCES thread(threadID) ON DELETE CASCADE,
    CONSTRAINT unique_users UNIQUE (discID, threadID)
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
    subjectID VARCHAR(7) NOT NULL REFERENCES subjects(subjectID),
    question_data STATS_QUESTIONS NOT NULL,
    CHECK (stats_questions_check(question_data))
);
/* 20241, mdc119, (15, 10, 8) */

CREATE TABLE IF NOT EXISTS semester_users (
    mapID SERIAL PRIMARY KEY,
    semesterID BIGINT NOT NULL REFERENCES semester(semesterID),
    discID BIGINT NOT NULL REFERENCES users(discID)
);
