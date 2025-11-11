SET client_encoding TO 'UTF8';
\pset format unaligned
\pset tuples_only on
SELECT 'account='||COUNT(*) FROM account;
SELECT 'group='||COUNT(*) FROM "group";
SELECT 'group_member='||COUNT(*) FROM group_member;
SELECT 'ai_config='||COUNT(*) FROM ai_config;
SELECT 'ai_detail='||COUNT(*) FROM ai_detail;
SELECT 'system='||COUNT(*) FROM system;
SELECT 'algorithm='||COUNT(*) FROM algorithm;
SELECT 'checklist='||COUNT(*) FROM checklist;
DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_class WHERE relname='checklist_item') THEN
  PERFORM 1; RAISE NOTICE 'checklist_item=%', (SELECT COUNT(*) FROM checklist_item);
ELSE RAISE NOTICE 'checklist_item=%', -1; END IF; END $$;
SELECT 'chat_history='||COUNT(*) FROM chat_history;
SELECT 'ai_learning='||COUNT(*) FROM ai_learning;
