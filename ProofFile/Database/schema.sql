-- Cria a tabela de usuários
CREATE TABLE users (
    id SERIAL,                         -- ID gerado automaticamente
    name VARCHAR NOT NULL,             -- Nome do usuário
    email VARCHAR UNIQUE NOT NULL,     -- E-mail único e obrigatório
    PRIMARY KEY (id)                   -- Define o ID como chave primária
);

-- Cria a tabela de empresas
CREATE TABLE companies (
    id SERIAL,                              -- ID gerado automaticamente
    company_name VARCHAR UNIQUE NOT NULL,   -- Nome único e obrigatório
    PRIMARY KEY (id)                        -- Define o ID como chave primária
);

-- Cria a tabela de contratos
CREATE TABLE contracts (
    id SERIAL,                              -- ID gerado automaticamente
    verification_code VARCHAR UNIQUE NOT NULL, -- Código único para verificação
    contract_name VARCHAR NOT NULL,          -- Nome do contrato
    company_id INT NOT NULL,                 -- ID da empresa relacionada
    user_id INT NOT NULL,                    -- ID do usuário que cadastrou
    registration_date DATE NOT NULL,         -- Data de registro
    expiration_date DATE,                    -- Data de expiração (opcional)
    file_path VARCHAR NOT NULL,              -- Caminho do arquivo
    file_hash VARCHAR UNIQUE NOT NULL,       -- Hash único do arquivo
    solana_transaction VARCHAR UNIQUE NOT NULL, -- Transação única na Solana

    PRIMARY KEY (id),                        -- Define o ID como chave primária
    FOREIGN KEY (company_id) REFERENCES companies(id), -- Liga contrato à empresa
    FOREIGN KEY (user_id) REFERENCES users(id)         -- Liga contrato ao usuário
);

-- Insere um usuário de teste
INSERT INTO users (name, email)
VALUES ('Alice', 'alice@exemplo.com');

-- Insere uma empresa de teste
INSERT INTO companies (company_name)
VALUES ('Tech Solutions');

-- Insere um contrato de teste
INSERT INTO contracts (verification_code, contract_name, company_id, user_id, registration_date, expiration_date, file_path, file_hash, solana_transaction)
VALUES ('VER-2026-0001', 'Contrato de Prestação de Serviços', 1, 1, '2026-10-02', '2027-10-02', '/contracts/contrato-0001.pdf', 'hash_teste_001', 'solana_tx_teste_001'
);

-- Mostra os usuários cadastrados
SELECT * FROM users;

-- Mostra as empresas cadastradas
SELECT * FROM companies;

-- Mostra os contratos cadastrados
SELECT * FROM contracts;

-- Consulta o contrato junto com os dados relacionados
SELECT ct.contract_name, cm.company_name, u.name, ct.registration_date, ct.expiration_date, ct.file_path, ct.file_hash, ct.solana_transaction 
FROM contracts AS ct INNER JOIN users AS u -- Relaciona juntando o contrato ao usuário que o cadastrou
    ON ct.user_id = u.id INNER JOIN companies AS cm -- Relaciona juntando o contrato à empresa
    ON ct.company_id = cm.id;

SELECT
    id,
    verification_code,
    contract_name,
    registration_date,
    expiration_date,
    file_path,
    file_hash,
    solana_transaction
FROM contracts;