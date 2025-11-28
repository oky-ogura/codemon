"""
Auto-generated placeholder migration to restore migration graph integrity.

This migration intentionally contains no operations. It exists solely so that
the subsequent migration 0006_account_avatar can depend on ('accounts', '0005_...').

If you prefer a different resolution (recreate the original 0005 operations),
replace this file with the appropriate migration content.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_group_groupmember_remove_account_type"),
    ]

    operations = [
        # intentionally empty: placeholder to restore linear history
    ]