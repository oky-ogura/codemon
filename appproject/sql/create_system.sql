-- SQL: create_system.sql
-- Creates sequence and table `system` in the `codemon` database.
-- System management table

-- 1) Create sequence starting at 4000001 for system_id
CREATE SEQUENCE IF NOT EXISTS system_system_id_seq
    START WITH 4000001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create system table
CREATE TABLE IF NOT EXISTS system (
    system_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('system_system_id_seq'),
    user_id INTEGER NOT NULL,
    system_name VARCHAR(100) NOT NULL,
    system_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) Set sequence ownership to column
ALTER SEQUENCE system_system_id_seq OWNED BY system.system_id;

-- 4) Create foreign key constraint to account table (if needed)
-- ALTER TABLE system ADD CONSTRAINT fk_system_user_id 
-- FOREIGN KEY (user_id) REFERENCES account(user_id) ON DELETE CASCADE;

-- 5) Insert sample data (optional)
-- INSERT INTO system (user_id, system_name, system_description) 
-- VALUES (20000001, '進捗管理システム', '生徒の進捗を管理するシステム');