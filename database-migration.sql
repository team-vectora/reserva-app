CREATE TABLE User (
    codigo INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    ativo BOOLEAN NOT NULL,
    admin BOOLEAN NOT NULL
);

CREATE TABLE Sala (
    codigo INT AUTO_INCREMENT PRIMARY KEY,
    capacidade INT NOT NULL,
    tipo INT NOT NULL,
    descricao TEXT NOT NULL,
    ativo BOOLEAN NOT NULL
);

CREATE TABLE Reserva (
    codigo INT AUTO_INCREMENT PRIMARY KEY,
    codigo_usuario INT NOT NULL,
    codigo_sala INT NOT NULL,
    datetime_start DATETIME NOT NULL,
    datetime_end DATETIME NOT NULL,
    ativo BOOLEAN NOT NULL,
    FOREIGN KEY (codigo_usuario) REFERENCES User(codigo),
    FOREIGN KEY (codigo_sala) REFERENCES Sala(codigo)
);

INSERT INTO User (nome, email, senha, ativo, admin) VALUES
('André Araújo Silva', 'andre@email', '$2b$12$tE5PrN2mjVget08fEbe5EOQHFGVGeHJu07ojO2H7CJgQ..TeqVLg6', TRUE, TRUE),
('Laura Daguer', 'laura@email', '$2b$12$2ZFesGRTWcqCzUDOtPJLoeycV2.KnWPJmKU.mdgJfRc4S.yEhtn4e', TRUE, TRUE),
('joao', 'joao@email', '$2b$12$WrqnC7ypGVYrewHZ4hF01.ukNd4PBOv4S.I4XuyrD15xW5DbIX9Sm', TRUE, FALSE);

INSERT INTO Sala (capacidade, tipo, descricao, ativo) VALUES
(30, 2, 'Sala com 4 professores para venda, mais 15 cobertores quentinhos, 5 fio denteais e 3 luvas de machado de assis', TRUE),
(10, 1, 'Sala com trez computadors', FALSE),
(25, 3, 'asdasdasdasdas', TRUE),
(40, 3, 'sala de aula maneira', TRUE),
(60, 1, 'uau que sala grande', TRUE);

INSERT INTO Reserva (codigo_sala, codigo_usuario, datetime_start, datetime_end, ativo) VALUES
(4, 1, '2024-08-08 21:40:00', '2024-08-08 23:40:00', TRUE),
(4, 1, '2024-08-06 21:40:00', '2024-08-06 22:40:00', TRUE),
(1, 2, '2024-08-01 07:40:00', '2024-08-01 09:40:00', TRUE);