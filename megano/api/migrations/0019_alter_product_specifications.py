# Generated by Django 4.2.1 on 2023-06-04 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_product_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='specifications',
            field=models.ManyToManyField(blank=True, default=[], related_name='products', to='api.specification'),
        ),
    ]
