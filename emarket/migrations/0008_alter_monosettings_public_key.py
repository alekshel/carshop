# Generated by Django 4.2.6 on 2024-01-15 16:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("emarket", "0007_remove_orderinvoice_orders_orderinvoice_orders"),
    ]

    operations = [
        migrations.AlterField(
            model_name="monosettings",
            name="public_key",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]