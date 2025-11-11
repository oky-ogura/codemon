-- SQL: create_checklist_item.sql
-- Creates sequence and table `checklist_item` for the codemon database.
-- Checklist item table (子テーブル)

-- 1) Create sequence starting at 6001001 for checklist_item_id
CREATE SEQUENCE IF NOT EXISTS checklist_item_checklist_item_id_seq
    START WITH 6001001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create checklist_item table
CREATE TABLE IF NOT EXISTS checklist_item (
    checklist_item_id BIGINT NOT NULL PRIMARY KEY DEFAULT nextval('checklist_item_checklist_item_id_seq'),
    checklist_id INTEGER NOT NULL REFERENCES checklist(checklist_id) ON DELETE CASCADE,
    item_text TEXT NOT NULL,
    is_done BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) Set sequence ownership
ALTER SEQUENCE checklist_item_checklist_item_id_seq OWNED BY checklist_item.checklist_item_id;

-- 4) Optional: index for faster lookup by checklist_id
CREATE INDEX IF NOT EXISTS idx_checklist_item_checklist_id
    ON checklist_item (checklist_id);
