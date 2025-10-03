-- PostgreSQL: create_ai_detail.sql
-- Creates table `ai_detail` in the `codemon` database.
-- AI detail management table for storing AI character settings and appearance

-- 1) Create ai_detail table
CREATE TABLE IF NOT EXISTS ai_detail (
    ai_setting_id INTEGER NOT NULL PRIMARY KEY,
    appearance VARCHAR(100) NOT NULL,
    ai_name VARCHAR(50) NOT NULL,
    ai_personality VARCHAR(100) NOT NULL,
    ai_speech VARCHAR(50),
    ai_image VARCHAR(100) NOT NULL
);

-- 2) Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_detail_ai_name ON ai_detail(ai_name);
CREATE INDEX IF NOT EXISTS idx_ai_detail_ai_personality ON ai_detail(ai_personality);
CREATE INDEX IF NOT EXISTS idx_ai_detail_appearance ON ai_detail(appearance);

-- 3) Create foreign key constraint
-- Note: Uncomment when ai_config table is created
-- ALTER TABLE ai_detail ADD CONSTRAINT fk_ai_detail_ai_setting_id 
-- FOREIGN KEY (ai_setting_id) REFERENCES ai_config(ai_setting_id) ON DELETE CASCADE;

-- 4) Create check constraints for data validation
ALTER TABLE ai_detail ADD CONSTRAINT chk_ai_detail_appearance 
CHECK (appearance IN ('三角', '四角', '丸', '星', 'triangle', 'square', 'circle', 'star'));

ALTER TABLE ai_detail ADD CONSTRAINT chk_ai_detail_ai_image 
CHECK (ai_image IN ('丸形', '四角形', '三角形', '星形', 'circle', 'square', 'triangle', 'star', 'custom'));

-- 5) Create default values constraints
ALTER TABLE ai_detail ALTER COLUMN ai_speech SET DEFAULT 'です';

-- 6) Insert sample data (optional)
-- INSERT INTO ai_detail (ai_setting_id, appearance, ai_name, ai_personality, ai_speech, ai_image) VALUES 
-- (1, '三角', 'codemon', '元気', 'です', '丸形'),
-- (2, '丸', 'サポートAI', 'やさしい', 'ですね', '四角形'),
-- (3, '四角', 'ヘルパー', 'まじめ', 'である', '三角形');

-- 7) Create view for AI character profiles
CREATE OR REPLACE VIEW ai_character_profile AS
SELECT 
    ad.ai_setting_id,
    ad.ai_name,
    ad.appearance,
    ad.ai_personality,
    ad.ai_speech,
    ad.ai_image,
    CASE 
        WHEN ad.ai_personality LIKE '%元気%' THEN 'アクティブ'
        WHEN ad.ai_personality LIKE '%やさしい%' THEN 'フレンドリー'
        WHEN ad.ai_personality LIKE '%まじめ%' THEN 'プロフェッショナル'
        ELSE 'その他'
    END as personality_category
FROM ai_detail ad
ORDER BY ad.ai_setting_id;

-- 8) Create function to get random AI speech pattern
CREATE OR REPLACE FUNCTION get_ai_speech_pattern(p_ai_setting_id INTEGER)
RETURNS VARCHAR(50) AS $$
DECLARE
    speech_pattern VARCHAR(50);
BEGIN
    SELECT ai_speech INTO speech_pattern
    FROM ai_detail
    WHERE ai_setting_id = p_ai_setting_id;
    
    RETURN COALESCE(speech_pattern, 'です');
END;
$$ LANGUAGE plpgsql;

-- 9) Create function to update AI personality
CREATE OR REPLACE FUNCTION update_ai_personality(
    p_ai_setting_id INTEGER,
    p_new_personality VARCHAR(100)
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE ai_detail 
    SET ai_personality = p_new_personality
    WHERE ai_setting_id = p_ai_setting_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- 10) Create trigger for data validation
CREATE OR REPLACE FUNCTION validate_ai_detail()
RETURNS TRIGGER AS $$
BEGIN
    -- AI名前の長さチェック
    IF LENGTH(NEW.ai_name) < 1 THEN
        RAISE EXCEPTION 'AI名前は1文字以上である必要があります';
    END IF;
    
    -- AI性格の長さチェック
    IF LENGTH(NEW.ai_personality) < 1 THEN
        RAISE EXCEPTION 'AI性格は1文字以上である必要があります';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_ai_detail
    BEFORE INSERT OR UPDATE ON ai_detail
    FOR EACH ROW
    EXECUTE FUNCTION validate_ai_detail();

-- 11) Comments for table and columns
COMMENT ON TABLE ai_detail IS 'AI詳細テーブル - AIキャラクターの設定と外見を管理';
COMMENT ON COLUMN ai_detail.ai_setting_id IS 'AI設定ID - 主キー、AI設定テーブルを参照する外部キー';
COMMENT ON COLUMN ai_detail.appearance IS 'AI外見 - AIの基本的な形状（三角、四角、丸、星など）';
COMMENT ON COLUMN ai_detail.ai_name IS 'AI名前 - AIキャラクターの名前';
COMMENT ON COLUMN ai_detail.ai_personality IS 'AI性格 - AIの性格設定（元気、やさしい、まじめなど）';
COMMENT ON COLUMN ai_detail.ai_speech IS 'AI語尾 - AIの話し方の特徴（です、ですね、であるなど）';
COMMENT ON COLUMN ai_detail.ai_image IS 'AI画像 - AIの表示画像の種類（丸形、四角形、三角形など）';

COMMENT ON VIEW ai_character_profile IS 'AIキャラクタープロフィールビュー - AIの特性を分類して表示';
COMMENT ON FUNCTION get_ai_speech_pattern IS 'AI語尾取得関数 - 指定されたAIの語尾パターンを取得';
COMMENT ON FUNCTION update_ai_personality IS 'AI性格更新関数 - AIの性格設定を更新';