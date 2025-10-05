DROP TABLE IF EXISTS preventivo_auto;
DROP TABLE IF EXISTS preventivo_casa;

-- DEFINIZIONE TABELLA PER INFORMAZIONI DELLA CASA --
CREATE TABLE IF NOT EXISTS preventivo_casa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_campo TEXT NOT NULL,
    fase INTEGER,
    opzioni TEXT,
    obbligatorio INTEGER,
    UNIQUE(nome_campo, fase, opzioni, obbligatorio)
);

-- DEFINIZIONE TABELLA PER INFORMAZIONI DELL'AUTO --
CREATE TABLE IF NOT EXISTS preventivo_auto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_campo TEXT NOT NULL,
    fase INTEGER,
    opzioni TEXT,
    obbligatorio INTEGER,
    UNIQUE(nome_campo, fase, opzioni, obbligatorio)
);

INSERT OR IGNORE INTO preventivo_casa(nome_campo, fase, opzioni, obbligatorio) VALUES
('Metri Quadri', 1, NULL, 1),
('Tipologia Abitazione', 1, '(Appartamento, Villa, Bilocale)', 0),
('Nome Proprietario', 2, NULL, 1),
('Cognome Proprietario',2, NULL, 1),
('Email Proprietario', 2, NULL, 1),
('Anno di costruzione', 3, NULL, 1),
('Uso Abitazione', 3, '(Residenziale, Professionale, Commerciale, Sociale, Agricolo, Ibrido)', 0);


INSERT OR IGNORE INTO preventivo_auto(nome_campo, fase, opzioni, obbligatorio) VALUES
('Tipologia Macchina', 1, 'Tendina(SUV, Utilitaria, Berlina, Monovolume, Coupé, Cabriolet, Van)', 1),
('Targa', 1, NULL, 1),
('Cilindrata', 1, NULL, 0),
('Nome Proprietario', 2, NULL, 1),
('Cognome Proprietario', 2, NULL, 1),
('Email Proprietario', 2, NULL, 1);


