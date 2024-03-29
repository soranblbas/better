# Generated by Django 4.1.7 on 2024-01-06 15:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_alter_openingbalance_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="saleinvoice",
            name="price_type",
            field=models.CharField(
                choices=[
                    ("مدفوع", "مدفوع"),
                    ("غير مدفوع", "غير مدفوع"),
                    ("المردود", "المردود"),
                ],
                default="IQD",
                max_length=10,
            ),
        ),
    ]
