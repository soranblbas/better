# Generated by Django 4.1.7 on 2024-01-06 15:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_saleinvoice_price_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="saleinvoice",
            name="price_type",
            field=models.CharField(
                choices=[("IQD", "IQD"), ("$", "$")], default="IQD", max_length=10
            ),
        ),
    ]
