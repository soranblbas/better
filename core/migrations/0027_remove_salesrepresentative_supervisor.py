# Generated by Django 4.1.7 on 2024-04-03 06:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_salesrepresentative_address_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesrepresentative',
            name='supervisor',
        ),
    ]
