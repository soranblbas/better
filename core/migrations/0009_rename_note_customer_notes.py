# Generated by Django 4.1.7 on 2023-12-11 11:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_customer_open_balance"),
    ]

    operations = [
        migrations.RenameField(
            model_name="customer",
            old_name="note",
            new_name="notes",
        ),
    ]