# Generated by Django 4.2.1 on 2023-06-15 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_alter_product_price'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Basket',
        ),
    ]
