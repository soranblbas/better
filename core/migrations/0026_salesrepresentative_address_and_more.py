# Generated by Django 4.1.7 on 2024-04-03 06:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_salesrepresentative_customer_sales_representative'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesrepresentative',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='salesrepresentative',
            name='department',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='salesrepresentative',
            name='joining_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='salesrepresentative',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='salesrepresentative',
            name='supervisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinates', to='core.salesrepresentative'),
        ),
        migrations.AlterField(
            model_name='salesrepresentative',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
    ]