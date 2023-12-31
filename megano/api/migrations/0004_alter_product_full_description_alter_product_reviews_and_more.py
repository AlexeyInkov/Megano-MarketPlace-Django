# Generated by Django 4.2.1 on 2023-06-02 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_category_options_alter_subcategory_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='full_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='reviews',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='reviews', to='api.review'),
        ),
        migrations.AlterField(
            model_name='product',
            name='specifications',
            field=models.ManyToManyField(blank=True, related_name='specifications', to='api.specification'),
        ),
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='tags', to='api.tag'),
        ),
    ]
