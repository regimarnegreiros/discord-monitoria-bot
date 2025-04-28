/* 2o a ser executado */

CREATE TABLE IF NOT EXISTS subjects (
    subjectID VARCHAR(7) PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    questions_data STATS_QUESTIONS NOT NULL,
    CHECK (stats_questions_check(questions_data))
);

CREATE TABLE IF NOT EXISTS users (
    discID BIGINT PRIMARY KEY,
    is_monitor BOOLEAN NOT NULL,
    questions_data STATS_QUESTIONS NOT NULL,
    monitor_data MONITOR_STATS,
    CHECK (stats_questions_check(questions_data)),
    CHECK (monitor_data_check(monitor_data))
);

CREATE TABLE IF NOT EXISTS thread ( /* thread de duvida */
    threadID BIGINT UNIQUE,
    threadCreatorID BIGINT NOT NULL,
    creationDate TIMESTAMP NOT NULL,
    PRIMARY KEY (threadID, threadCreatorID),
    FOREIGN KEY (threadCreatorID) REFERENCES users(discID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    tagID BIGINT PRIMARY KEY,
    tag_name VARCHAR(50) UNIQUE NOT NULL,
    subjectID VARCHAR(7) UNIQUE REFERENCES subjects(subjectID)
);

CREATE TABLE IF NOT EXISTS semester (
    semesterID SERIAL PRIMARY KEY,
    semester_year INT,
    semester INT,
    monitors JSONB,
    subject_data JSONB,
    CHECK (semester BETWEEN 1 AND 2),
    CHECK (semester_year >= 2023),
    CONSTRAINT proper_pair UNIQUE (semester_year, semester)
);
