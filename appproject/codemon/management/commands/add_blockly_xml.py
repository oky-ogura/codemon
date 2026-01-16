# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Add blockly_xml column to algorithm table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # まずカラムが存在するか確認
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pragma_table_info('algorithm') 
                    WHERE name='blockly_xml';
                """)
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    self.stdout.write(self.style.WARNING('Column blockly_xml already exists'))
                else:
                    # blockly_xml カラムを追加
                    cursor.execute("""
                        ALTER TABLE algorithm
                        ADD COLUMN blockly_xml TEXT;
                    """)
                    
                    self.stdout.write(self.style.SUCCESS('Successfully added blockly_xml column to algorithm table'))
                
                # カラムが追加されたか確認
                cursor.execute("""
                    SELECT name, type 
                    FROM pragma_table_info('algorithm') 
                    WHERE name='blockly_xml';
                """)
                result = cursor.fetchone()
                
                if result:
                    self.stdout.write(self.style.SUCCESS(f'Verified: Column {result[0]} exists with type {result[1]}'))
                else:
                    self.stdout.write(self.style.WARNING('Column verification failed'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {e}'))
                raise
