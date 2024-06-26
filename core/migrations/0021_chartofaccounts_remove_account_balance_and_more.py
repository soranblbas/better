# Generated by Django 4.1.7 on 2024-04-02 06:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_account_transaction_alter_item_price_list_entry'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChartOfAccounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='اسم الحساب')),
            ],
        ),
        migrations.RemoveField(
            model_name='account',
            name='balance',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='description',
        ),
        migrations.AddField(
            model_name='transaction',
            name='account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.account', verbose_name='الحساب'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10, verbose_name='المبلغ'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='name',
            field=models.CharField(max_length=100, verbose_name='اسم الحساب'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateField(auto_now_add=True, verbose_name='التاريخ'),
        ),
        migrations.DeleteModel(
            name='Entry',
        ),
        migrations.AddField(
            model_name='account',
            name='chart_of_account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.chartofaccounts', verbose_name='القائمة'),
            preserve_default=False,
        ),
    ]
