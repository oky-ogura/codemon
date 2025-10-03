-- SQL: create_algorithm.sql
-- Creates sequence and table `algorithm` in the `codemon` database.
-- Algorithm management table

-- 1) Create sequence starting at 5000001 for algorithm_id
CREATE SEQUENCE IF NOT EXISTS algorithm_algorithm_id_seq
    START WITH 5000001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create algorithm table
CREATE TABLE IF NOT EXISTS algorithm (
    algorithm_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('algorithm_algorithm_id_seq'),
    user_id INTEGER NOT NULL,
    algorithm_name VARCHAR(100) NOT NULL,
    algorithm_description TEXT DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) Set sequence ownership to column
ALTER SEQUENCE algorithm_algorithm_id_seq OWNED BY algorithm.algorithm_id;

-- 4) Create foreign key constraint to account table (if needed)
-- ALTER TABLE algorithm ADD CONSTRAINT fk_algorithm_user_id 
-- FOREIGN KEY (user_id) REFERENCES account(user_id) ON DELETE CASCADE;

-- 5) Insert sample data (optional)
-- INSERT INTO algorithm (user_id, algorithm_name, algorithm_description) 
-- VALUES (20000001, '進捗判定アルゴリズム', '進捗を自動判定するアルゴリズム');