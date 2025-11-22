#!/usr/bin/env python
import sys
import os

# Djangoの設定を読み込む
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')

import django
django.setup()

from django.db import connection

# SQLを実行
with connection.cursor() as cursor:
    try:
        # avatarカラムを追加
        cursor.execute("ALTER TABLE account ADD COLUMN IF NOT EXISTS avatar VARCHAR(100) NULL")
        print("✓ avatarカラムを追加しました")
        
        # account_typeカラムを追加
        cursor.execute("ALTER TABLE account ADD COLUMN IF NOT EXISTS account_type VARCHAR(20) NULL")
        print("✓ account_typeカラムを追加しました")
        
        # 確認
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name='account' 
            AND column_name IN ('avatar', 'account_type')
            ORDER BY column_name
        """)
        
        print("\n確認結果:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} (NULL許可: {row[2]})")
        
        print("\n✓ 完了")
    except Exception as e:
        print(f"✗ エラー: {e}")
        sys.exit(1)
