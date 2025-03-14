-- PostgreSQL
-- 1o a ser executado

CREATE TYPE STATS_QUESTIONS AS (
    total INT,
    answered INT,
    solved INT
);

CREATE OR REPLACE FUNCTION stats_questions_check(questions_data STATS_QUESTIONS)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (questions_data.total >= questions_data.answered) AND 
           (questions_data.answered >= questions_data.solved) AND
           (questions_data.solved >= 0);
END;
$$
LANGUAGE plpgsql;

SET client_min_messages TO WARNING;
