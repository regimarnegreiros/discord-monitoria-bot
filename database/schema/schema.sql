-- 2o a ser executado
\c db_monitoria

CREATE TABLE IF NOT EXISTS materia (
    materiaID INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    dados STATS_DUVIDAS NOT NULL,
    CHECK (stats_duvidas_check(dados))
); -- ex.: (15, POO, (0, 0, 0)); on_new_semester: export dados somewhere, 0's on original materia(dados)

CREATE TABLE IF NOT EXISTS usuario (
    discID INT PRIMARY KEY,
    monitoria BOOLEAN NOT NULL,
    dados STATS_DUVIDAS NOT NULL,
    CHECK (stats_duvidas_check(dados))
);

CREATE TABLE IF NOT EXISTS thread ( -- thread de duvida
    threadID INT UNIQUE,
    threadCreatorID INT,
    creationDate DATE NOT NULL,
    PRIMARY KEY (threadID, threadCreatorID),
    FOREIGN KEY (threadCreatorID) REFERENCES usuario(discID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    tagID INT PRIMARY KEY,
    nome VARCHAR(50) UNIQUE NOT NULL,
    threadID INT NOT NULL,
    materiaID INT UNIQUE,
    FOREIGN KEY (materiaID) REFERENCES materia(materiaID)
);

CREATE TABLE IF NOT EXISTS semestre (
    semestreID SERIAL PRIMARY KEY,
    ano INT,
    semestre INT,
    CHECK (semestre BETWEEN 1 AND 2),
    CHECK (ano >= 2023)
);
