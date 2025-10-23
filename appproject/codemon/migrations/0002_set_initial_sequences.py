from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codemon', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "DO $$ BEGIN "
                "IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='checklist') THEN "
                "PERFORM setval(pg_get_serial_sequence('checklist','checklist_id'), 6000000, false); "
                "END IF; "
                "IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='checklist_item') THEN "
                "PERFORM setval(pg_get_serial_sequence('checklist_item','checklist_item_id'), 6001000, false); "
                "END IF; "
                "END $$;"
            ),
            reverse_sql=(
                "DO $$ BEGIN "
                "IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='checklist') THEN "
                "PERFORM setval(pg_get_serial_sequence('checklist','checklist_id'), (SELECT COALESCE(MAX(checklist_id),0) FROM checklist), true); "
                "END IF; "
                "IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='checklist_item') THEN "
                "PERFORM setval(pg_get_serial_sequence('checklist_item','checklist_item_id'), (SELECT COALESCE(MAX(checklist_item_id),0) FROM checklist_item), true); "
                "END IF; "
                "END $$;"
            )
        ),
    ]
