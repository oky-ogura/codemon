"""
Empty placeholder migration to satisfy historical branch that referenced
`0002_account_avatar`. Some environments used a migration that added an
`avatar` field; that file is not present in this tree, but other merge
migrations reference it. Creating a no-op migration unblocks Django's
migration graph validation while preserving history.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        # Intentionally empty: placeholder to satisfy merge dependency
    ]
