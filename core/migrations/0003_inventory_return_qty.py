# Generated by Django 4.2 on 2023-05-10 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_saleitem_options_saleitem_is_returned"),
    ]

    operations = [
        migrations.AddField(
            model_name="inventory",
            name="return_qty",
            field=models.FloatField(default=0),
        ),
    ]
