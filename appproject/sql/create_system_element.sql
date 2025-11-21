-- SQL: create_system_element.sql
-- Creates sequence and table `system_element` in the `codemon` database.
-- System element management table for storing UI components

-- 1) Create sequence starting at 7000001 for element_id
CREATE SEQUENCE IF NOT EXISTS system_element_element_id_seq
    START WITH 7000001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create system_element table
CREATE TABLE IF NOT EXISTS system_element (
    element_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('system_element_element_id_seq'),
    system_id INTEGER NOT NULL,
    element_type VARCHAR(50) NOT NULL,
    element_label VARCHAR(200),
    element_value TEXT,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    width INTEGER,
    height INTEGER,
    style_data JSONB,
    element_config JSONB,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) Set sequence ownership to column
ALTER SEQUENCE system_element_element_id_seq OWNED BY system_element.element_id;

-- 4) Create foreign key constraint to system table
ALTER TABLE system_element ADD CONSTRAINT fk_system_element_system_id 
FOREIGN KEY (system_id) REFERENCES system(system_id) ON DELETE CASCADE;

-- 5) Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_system_element_system_id ON system_element(system_id);
CREATE INDEX IF NOT EXISTS idx_system_element_type ON system_element(element_type);

-- 6) Add comments for documentation
COMMENT ON TABLE system_element IS 'システム画面の各UI要素を保存するテーブル';
COMMENT ON COLUMN system_element.element_id IS '要素ID（主キー、7000001から開始）';
COMMENT ON COLUMN system_element.system_id IS 'システムID（外部キー）';
COMMENT ON COLUMN system_element.element_type IS '要素タイプ（text_input, number_input, datetime_input, checkbox_group, radio_group, button, text_box）';
COMMENT ON COLUMN system_element.element_label IS '要素のラベル（例：「文字：」「数字：」など）';
COMMENT ON COLUMN system_element.element_value IS '要素のデフォルト値やプレースホルダー';
COMMENT ON COLUMN system_element.position_x IS 'X座標位置';
COMMENT ON COLUMN system_element.position_y IS 'Y座標位置';
COMMENT ON COLUMN system_element.width IS '要素の幅（ピクセル）';
COMMENT ON COLUMN system_element.height IS '要素の高さ（ピクセル）';
COMMENT ON COLUMN system_element.style_data IS 'スタイル情報（JSON形式、color, background-color, font-size等）';
COMMENT ON COLUMN system_element.element_config IS '要素固有の設定（JSON形式、チェックボックス数、ボタン遷移先等）';
COMMENT ON COLUMN system_element.sort_order IS '表示順序';
