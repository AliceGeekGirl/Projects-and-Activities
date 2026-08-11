
-- Cria a tabela de estudantes da biblioteca
CREATE TABLE alunos (
  id_aluno INT,    
  cpf VARCHAR UNIQUE, -- CPF salvo como texto para aceitar pontos e traço
  matricula INT UNIQUE, -- Matrícula única por estudante
  nome VARCHAR(50) NOT NULL, -- Nome obrigatório com limite de 50 caracteres
  curso VARCHAR NOT NULL, -- Curso obrigatório do aluno
  email VARCHAR UNIQUE, -- E-mail único para evitar duplicados
  PRIMARY KEY (id_aluno) -- Define o id_aluno como a chave principal
);

-- Cria a tabela para os livros da biblioteca
CREATE TABLE livro (
  codigo SERIAL, -- SERIAL gera números automáticos (1, 2, 3...) no Postgres
  titulo VARCHAR NOT NULL,
  editora VARCHAR NOT NULL,
  nr_paginas INT NOT NULL,
  isbn VARCHAR UNIQUE, -- Código internacional exclusivo do livro
  ano_publicacao INT NOT NULL, 
  qtde_disponivel INT NOT NULL,
  PRIMARY KEY (codigo) -- O código gerado vira a chave primária
); 

-- Cria a tabela com as informações dos escritores
CREATE TABLE autor (
  id_autor INT,
  nome VARCHAR(50) NOT NULL,
  pais VARCHAR,
  PRIMARY KEY (id_autor) -- Define o id_autor como chave primária
);

-- Tabela intermediária para ligar Livros aos seus Autores (Muitos para Muitos)
CREATE TABLE livro_autor (
  codigo_livro INT,
  id_autor INT,
  PRIMARY KEY (codigo_livro, id_autor), -- Chave primária composta (evita repetir o mesmo vínculo)
  FOREIGN KEY (codigo_livro) REFERENCES livro(codigo), -- Garante que o livro existe na tabela livro
  FOREIGN KEY (id_autor) REFERENCES autor(id_autor) -- Garante que o autor existe na tabela autor
);

-- Cria a tabela para registrar o histórico de empréstimos
CREATE TABLE emprestimo (
  id_emprestimo INT,
  data_emprestimo DATE NOT NULL, -- Formato de data nativo (AAAA-MM-DD)
  data_devolucao_prevista DATE,
  data_devolucao_real DATE, -- Pode ficar vazia (NULL) se o livro ainda não voltou
  id_aluno INT, -- Coluna para identificar quem pegou
  codigo_livro INT, -- Coluna para identificar qual livro levou
  PRIMARY KEY (id_emprestimo),
  FOREIGN KEY (id_aluno) REFERENCES alunos(id_aluno), -- Liga com a tabela alunos
  FOREIGN KEY (codigo_livro) REFERENCES livro(codigo) -- Liga com a tabela livro
);

-- Altera o tipo da coluna CPF para garantir que ela aceite textos longos (VARCHAR)
ALTER TABLE alunos
ALTER COLUMN cpf TYPE varchar;

-- Remove a coluna de telefone da tabela de alunos
ALTER TABLE alunos
DROP COLUMN telefone;

-- Insere os primeiros 3 estudantes de teste
INSERT INTO alunos (id_aluno, cpf, matricula, nome, curso, email)
VALUES (1, '368.896.908-99', 202422, 'Alex', 'Psicologia', 'alex@gmail.com'),
(2, '769.906.234-67', 202455, 'Julia', 'Artes', 'julia@gmail.com'),
(3, '657.900.222-89', 202244, 'Fernando', 'Mecânica', 'fernando@gmail.com');

-- Insere 3 grandes títulos literários (os códigos 1, 2 e 3 vão gerar sozinhos por causa do SERIAL)
INSERT INTO livro (titulo, editora, nr_paginas, isbn, ano_publicacao, qtde_disponivel)
VALUES ('Senhor dos Aneis', 'Artenova', 1202, '09786555112511', 1954, 10),
('Código Limpo', 'Alta Books', 425, '978-8576082675', 2009, 5),
('Harry Potter e a Pedra Filosofal', 'Rocco', 264, '978-8532511010', 2000, 10);

-- Insere os escritores associados
INSERT INTO autor(id_autor, nome, pais)
VALUES (1, 'J. R. R. Tolkien', 'África do Sul'),
(2,'Robert C. Martin', 'Estados Unidos'),
(3,'J.K. Rowling', 'Reino Unido');

-- Vincula cada livro cadastrado ao seu respectivo autor cadastrado
INSERT INTO livro_autor(codigo_livro, id_autor)
VALUES (1,1), 
(2,2), 
(3,3);

-- Registra 3 situações reais de empréstimo de livros
INSERT INTO emprestimo(id_emprestimo, data_emprestimo, data_devolucao_prevista, data_devolucao_real, id_aluno, codigo_livro)
VALUES (1, '2026-03-10', '2026-03-17', '2026-03-15', 3, 1), -- Fernando devolveu no prazo
(2, '2026-07-12', '2026-07-19', NULL, 1, 2), -- Alex está com o livro em mãos atualmente (Devolucao NULL)
(3, '2026-06-25', '2026-07-05', '2026-07-10', 1, 3); -- Alex devolveu com atraso


-- Comandos rápidos para verificar os dados salvos em cada tabela
SELECT * FROM alunos;
SELECT * FROM livro;
SELECT * FROM autor;
SELECT * FROM livro_autor;
SELECT * FROM emprestimo;

-- Desafio 1: Escreva um comando para listar apenas os alunos que fazem o curso de 'Psicologia'

SELECT nome, curso FROM alunos
WHERE curso = 'Psicologia';

-- Desafio 2: Escreva uma consulta que traga apenas os livros que tenham mais de 400 páginas.

SELECT titulo, nr_paginas FROM livro
WHERE nr_paginas > 400;

-- Desafio 3 (Livro específico): Mostre as informações do livro cujo codigo seja igual a 2.

SELECT * FROM livro
WHERE codigo = 2;

-- Desafio 4 (Estoque): Busque os livros que têm mais de 350 páginas E que foram publicados depois do ano 2000.

SELECT * FROM livro
WHERE nr_paginas > 350 AND ano_publicacao > 2000;

-- Desafio 5 (Busca de texto parcialmente): Busque na tabela autor qualquer escritor cujo nome comece com a letra 'J' (Dica: use o operador LIKE 'J%').

SELECT * FROM autor
WHERE nome LIKE 'J%';

-- Desafio 6 (Empréstimos pendentes): Liste todos os empréstimos onde a data_devolucao_real é nula (ou seja, IS NULL), indicando que o livro ainda não foi devolvido.

SELECT * FROM emprestimo
WHERE data_devolucao_real IS NULL; -- Filtra registros onde a data de devolução está vazia (nula)

-- Desafio 7 (Organizar ordem): Mostre todos os livros cadastrados, mas organizados do mais novo para o mais antigo (ordem decrescente de ano_publicacao).

SELECT * FROM livro
ORDER BY ano_publicacao DESC;

-- Desafio 8: Adicionar data_cadastro na tabela alunos

ALTER TABLE alunos -- Informa que a tabela autor será alterada
ADD COLUMN data_cadastro DATE DEFAULT CURRENT_DATE; -- Cria a coluna data_cadastro que pega a data atual automaticamente

-- Desafio 9: Renomear coluna na tabela autor
ALTER TABLE autor 
RENAME COLUMN pais TO pais_origem; -- Altera o nome da coluna pais para pais_origem

-- Desafio 10: Alterar tamanho do titulo na tabela livro
ALTER TABLE livro 
ALTER COLUMN titulo TYPE VARCHAR(150); -- Modifica o tipo e limite de tamanho da coluna titulo

-- Desafio 11: Definir NOT NULL na coluna pais_origem da tabela autor
ALTER TABLE autor 
ALTER COLUMN pais_origem SET NOT NULL; -- Aplica a restrição para não permitir valores nulos na coluna

-- Desafio 12: Adicionar categoria e remover nr_paginas em um único ALTER TABLE
ALTER TABLE livro 
ADD COLUMN categoria VARCHAR(30), -- Adiciona a nova coluna categoria com limite de 30 caracteres
DROP COLUMN nr_paginas; -- Remove permanentemente a coluna nr_paginas da tabela