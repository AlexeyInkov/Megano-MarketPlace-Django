# Generated by Django 4.2.1 on 2023-06-06 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_rename_product_sold_product_sold'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='reviews',
            field=models.IntegerField(default=0),
        ),
    ]
