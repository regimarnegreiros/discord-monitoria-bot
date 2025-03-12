-- 3o a ser executado
\c db_monitoria;

CREATE TABLE IF NOT EXISTS usuario_thread (
    mapID SERIAL PRIMARY KEY,
    discID INT REFERENCES usuario(discID) ON UPDATE CASCADE ON DELETE CASCADE,
    threadID INT REFERENCES thread(threadID) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tag_thread (
    mapID SERIAL PRIMARY KEY,
    tagID INT REFERENCES tags(tagID),
    threadID INT NOT NULL REFERENCES thread(threadID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS semestre_materia (
    mapID SERIAL PRIMARY KEY,
    semestreID INT NOT NULL REFERENCES semestre(semestreID),
    materiaID INT NOT NULL REFERENCES materia(materiaID),
    dados_materia_semestre STATS_DUVIDAS NOT NULL,
    CHECK (stats_duvidas_check(dados_materia_semestre))
);
