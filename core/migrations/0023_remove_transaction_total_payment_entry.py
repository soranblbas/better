# Generated by Django 4.1.7 on 2024-04-02 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_transaction_total_payment_entry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='total_payment_entry',
        ),
    ]