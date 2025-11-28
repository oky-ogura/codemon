-- SystemElementテーブルを作成
CREATE TABLE IF NOT EXISTS codemon_systemelement (
    element_id BIGSERIAL PRIMARY KEY,
    system_id BIGINT NOT NULL REFERENCES codemon_system(system_id) ON DELETE CASCADE,
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- element_idのシーケンスを7000001から開始
ALTER SEQUENCE codemon_systemelement_element_id_seq RESTART WITH 7000001;
