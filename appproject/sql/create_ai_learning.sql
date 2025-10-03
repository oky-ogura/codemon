-- PostgreSQL: create_ai_learning.sql
-- Creates sequence and table `ai_learning` in the `codemon` database.
-- AI learning data management table for storing training data and features

-- 1) Create sequence for auto-incrementing training_data_id
CREATE SEQUENCE IF NOT EXISTS ai_learning_training_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create ai_learning table
CREATE TABLE IF NOT EXISTS ai_learning (
    training_data_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('ai_learning_training_data_id_seq'),
    ai_setting_id INTEGER NOT NULL,
    data_name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    data_path VARCHAR(255),
    learned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    features JSONB,
    user_id INTEGER NOT NULL
);

-- 3) Set sequence ownership to column
ALTER SEQUENCE ai_learning_training_data_id_seq OWNED BY ai_learning.training_data_id;

-- 4) Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_learning_ai_setting_id ON ai_learning(ai_setting_id);
CREATE INDEX IF NOT EXISTS idx_ai_learning_user_id ON ai_learning(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_learning_data_type ON ai_learning(data_type);
CREATE INDEX IF NOT EXISTS idx_ai_learning_learned_at ON ai_learning(learned_at);
CREATE INDEX IF NOT EXISTS idx_ai_learning_data_name ON ai_learning(data_name);

-- 5) Create GIN index for JSONB features column
CREATE INDEX IF NOT EXISTS idx_ai_learning_features ON ai_learning USING GIN (features);

-- 6) Create foreign key constraints
-- Note: Uncomment when ai_config and account tables are created
-- ALTER TABLE ai_learning ADD CONSTRAINT fk_ai_learning_ai_setting_id 
-- FOREIGN KEY (ai_setting_id) REFERENCES ai_config(ai_setting_id) ON DELETE CASCADE;

-- ALTER TABLE ai_learning ADD CONSTRAINT fk_ai_learning_user_id 
-- FOREIGN KEY (user_id) REFERENCES account(user_id) ON DELETE CASCADE;

-- 7) Create check constraints for data validation
ALTER TABLE ai_learning ADD CONSTRAINT chk_ai_learning_data_type 
CHECK (data_type IN ('画像', 'テキスト', '音声', 'image', 'text', 'audio', 'video', 'document'));

-- 8) Create trigger for automatic learned_at update
CREATE OR REPLACE FUNCTION update_learned_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.learned_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ai_learning_learned_at 
    BEFORE UPDATE ON ai_learning 
    FOR EACH ROW EXECUTE FUNCTION update_learned_at_column();

-- 9) Insert sample data (optional)
-- INSERT INTO ai_learning (ai_setting_id, data_name, data_type, data_path, features, user_id) VALUES 
-- (1, 'プログラミング基礎データ', 'テキスト', '/data/programming_basics.txt', '{"keyword":"進捗","count":5}', 20000001),
-- (1, 'Python学習画像', '画像', '/data/python_tutorial.jpg', '{"language":"python","difficulty":"beginner"}', 20000001),
-- (2, 'Java演習問題', 'テキスト', '/data/java_exercises.txt', '{"keyword":"演習","count":10}', 20000002);

-- 10) Create view for learning data summary
CREATE OR REPLACE VIEW ai_learning_summary AS
SELECT 
    al.ai_setting_id,
    al.user_id,
    al.data_type,
    COUNT(*) as data_count,
    MAX(al.learned_at) as latest_learning,
    MIN(al.learned_at) as earliest_learning
FROM ai_learning al
GROUP BY al.ai_setting_id, al.user_id, al.data_type
ORDER BY al.ai_setting_id, al.user_id, al.data_type;

-- 11) Create function to search by features
CREATE OR REPLACE FUNCTION search_by_features(search_key TEXT, search_value TEXT DEFAULT NULL)
RETURNS TABLE(training_data_id INTEGER, data_name VARCHAR(100), features JSONB) AS $$
BEGIN
    IF search_value IS NULL THEN
        RETURN QUERY
        SELECT al.training_data_id, al.data_name, al.features
        FROM ai_learning al
        WHERE al.features ? search_key;
    ELSE
        RETURN QUERY
        SELECT al.training_data_id, al.data_name, al.features
        FROM ai_learning al
        WHERE al.features ->> search_key = search_value;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 12) Comments for table and columns
COMMENT ON TABLE ai_learning IS 'AI学習テーブル - 学習データと特徴量を管理';
COMMENT ON COLUMN ai_learning.training_data_id IS '学習データID - 主キー、学習データの一意識別子';
COMMENT ON COLUMN ai_learning.ai_setting_id IS 'AI設定ID - AI設定テーブルを参照する外部キー';
COMMENT ON COLUMN ai_learning.data_name IS 'データ名 - 学習データの名称';
COMMENT ON COLUMN ai_learning.data_type IS 'データ種別 - 画像/テキスト/音声などのデータタイプ';
COMMENT ON COLUMN ai_learning.data_path IS 'データパス - ファイルパスまたはURL';
COMMENT ON COLUMN ai_learning.learned_at IS '学習日時 - 最終更新日時（自動更新）';
COMMENT ON COLUMN ai_learning.features IS '特徴量 - JSON形式で格納される学習データの特徴';
COMMENT ON COLUMN ai_learning.user_id IS 'ユーザーID - アカウントテーブルを参照する外部キー';

COMMENT ON VIEW ai_learning_summary IS 'AI学習データサマリービュー - 学習データの統計情報';
COMMENT ON FUNCTION search_by_features IS '特徴量検索関数 - JSON特徴量から学習データを検索';