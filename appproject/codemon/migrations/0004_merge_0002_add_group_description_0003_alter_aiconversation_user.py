"""
Merge migration to resolve branching in codemon migrations.

This migration simply unifies two leaf nodes so Django's migration graph
is consistent. It has no operations.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("codemon", "0002_add_group_description"),
        ("codemon", "0003_alter_aiconversation_user"),
    ]

    operations = [
        # merge-only migration
    ]