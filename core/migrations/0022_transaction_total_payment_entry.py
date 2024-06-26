# Generated by Django 4.1.7 on 2024-04-02 07:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_chartofaccounts_remove_account_balance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='total_payment_entry',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='core.payment_entry', verbose_name='إدخال الدفع'),
            preserve_default=False,
        ),
    ]
