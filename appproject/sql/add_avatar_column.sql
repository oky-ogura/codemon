-- アバターとアカウントタイプのカラムを追加するSQL

-- avatarカラムが存在しない場合のみ追加
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'account' AND column_name = 'avatar'
    ) THEN
        ALTER TABLE account ADD COLUMN avatar VARCHAR(100) NULL;
    END IF;
END $$;

-- account_typeカラムが存在しない場合のみ追加
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'account' AND column_name = 'account_type'
    ) THEN
        ALTER TABLE account ADD COLUMN account_type VARCHAR(20) NULL;
    END IF;
END $$;

-- 確認
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'account' 
AND column_name IN ('avatar', 'account_type')
ORDER BY column_name;
