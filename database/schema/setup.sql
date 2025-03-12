-- PostgreSQL
-- 1o a ser executado

CREATE DATABASE db_monitoria;
\c db_monitoria;

CREATE TYPE STATS_DUVIDAS AS (
    total INT,
    respondidas INT,
    resolvidas INT
);

CREATE OR REPLACE FUNCTION stats_duvidas_check(dados STATS_DUVIDAS)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (dados.total >= dados.respondidas) AND 
           (dados.respondidas >= dados.resolvidas) AND
           (dados.resolvidas >= 0);
END;
$$
LANGUAGE plpgsql;
