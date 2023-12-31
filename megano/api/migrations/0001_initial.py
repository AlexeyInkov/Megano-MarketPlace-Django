# Generated by Django 4.2.1 on 2023-06-02 09:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(default=0)),
                ('count', models.IntegerField(default=0)),
                ('date', models.DateField(auto_now_add=True)),
                ('title', models.CharField(max_length=100)),
                ('free_delivery', models.BooleanField(default=False)),
                ('rating', models.FloatField(default=0)),
                ('full_description', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Specification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='image_subcat', to='api.image')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_price', models.FloatField(default=0)),
                ('dateFrom', models.DateField()),
                ('dateTo', models.DateField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(null=True)),
                ('rate', models.IntegerField(default=0)),
                ('date', models.DateField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=15, null=True)),
                ('avatar', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='avatar', to='api.image')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(default=0)),
                ('count', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product', to='api.product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='category', to='api.subcategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='images_prod', to='api.image'),
        ),
        migrations.AddField(
            model_name='product',
            name='reviews',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reviews', to='api.review'),
        ),
        migrations.AddField(
            model_name='product',
            name='specifications',
            field=models.ManyToManyField(related_name='specifications', to='api.specification'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tags', to='api.tag'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_at', models.DateField(auto_now_add=True)),
                ('delivery_type', models.CharField(max_length=100)),
                ('payment_type', models.CharField(max_length=100)),
                ('total_cost', models.FloatField()),
                ('status', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=250)),
                ('products', models.ManyToManyField(related_name='orders', to='api.productorder')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='image_cat', to='api.image')),
                ('subcategories', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subcategories', to='api.subcategory')),
            ],
        ),
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('products', models.ManyToManyField(related_name='baskets', to='api.productorder')),
            ],
        ),
    ]
