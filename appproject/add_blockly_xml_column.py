#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adds blockly_xml column to algorithm table directly using psycopg2
"""
import sys

def add_blockly_xml_column():
    """Add blockly_xml column to algorithm table"""
    try:
        import psycopg2
        
        # データベース接続（パスワードを直接指定）
        conn = psycopg2.connect(
            host='localhost',
            user='postgres',
            password='postgres',  # デフォルトパスワード
            dbname='codemon'
        )
        cursor = conn.cursor()
        
        # blockly_xml カラムを追加
        sql = """
        ALTER TABLE algorithm
        ADD COLUMN IF NOT EXISTS blockly_xml TEXT;
        """
        
        cursor.execute(sql)
        conn.commit()
        
        print("Successfully added blockly_xml column to algorithm table")
        
        # カラムが追加されたか確認
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'algorithm' AND column_name = 'blockly_xml';
        """)
        result = cursor.fetchone()
        
        if result:
            print("Verified: Column '{}' exists with type '{}'".format(result[0], result[1]))
        else:
            print("Warning: Column verification failed")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print("Database error: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = add_blockly_xml_column()
    sys.exit(0 if success else 1)
