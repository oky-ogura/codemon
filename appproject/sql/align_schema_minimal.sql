SET client_encoding TO 'UTF8';
BEGIN;
-- account にコード互換用の type 列を追加（存在しない場合のみ）
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='account' AND column_name='type'
  ) THEN
    ALTER TABLE account ADD COLUMN type VARCHAR(20);
    UPDATE account SET type = account_type;
  END IF;
END; $$;
COMMIT;
