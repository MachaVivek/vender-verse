# Generated by Django 5.0.4 on 2024-04-28 18:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0002_orderdetails"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderdetails",
            name="stripe_payment_intent",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]