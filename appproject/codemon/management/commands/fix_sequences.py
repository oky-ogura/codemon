from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix Postgres sequences for tables that use manual DB sequences (e.g. "group" primary key)'

    def handle(self, *args, **options):
        # This command sets the sequence for the group.group_id primary key
        # to the current MAX(group_id) so next INSERT will not clash.
        sql = (
            "SELECT setval(pg_get_serial_sequence('\"group\"','group_id'), "
            "COALESCE((SELECT MAX(group_id) FROM \"group\"), 1), true);"
        )
        with connection.cursor() as cur:
            try:
                cur.execute("SELECT pg_get_serial_sequence('\"group\"','group_id');")
                seq = cur.fetchone()[0]
                if not seq:
                    self.stdout.write(self.style.WARNING('No sequence found for table "group" column group_id'))
                else:
                    self.stdout.write(f'Found sequence: {seq}. Setting to MAX(group_id) ...')
                cur.execute(sql)
                self.stdout.write(self.style.SUCCESS('Sequence updated successfully.'))
            except Exception as e:
                self.stderr.write(str(e))
                raise
