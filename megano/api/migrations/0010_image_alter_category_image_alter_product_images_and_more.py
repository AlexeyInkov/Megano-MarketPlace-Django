# Generated by Django 4.2.1 on 2023-06-03 13:16

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_remove_category_subcategories_category_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.ImageField(upload_to=api.models.get_image_path)),
                ('alt', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category', to='api.image'),
        ),
        migrations.AlterField(
            model_name='product',
            name='images',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product', to='api.image'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='avatar', to='api.image'),
        ),
    ]
