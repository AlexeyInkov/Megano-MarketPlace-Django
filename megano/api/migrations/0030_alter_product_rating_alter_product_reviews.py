# Generated by Django 4.2.1 on 2023-06-06 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_product_rating_product_reviews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='rating',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='reviews',
            field=models.IntegerField(),
        ),
    ]
