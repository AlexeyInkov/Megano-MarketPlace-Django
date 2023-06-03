

from django.contrib.auth.models import User
from django.db import models


# TODO объеденить в одну функцию
def get_avatar_path(instance: 'Profile', filename: str) -> str:
    return 'image/avatar/{username}/{filename}'.format(
        username=instance.user.username,
        filename=filename)


def get_cat_path(instance, filename) -> str:
    return 'image/category/{title}/{filename}'.format(
        title=instance.title,
        filename=filename)


def get_product_path(instance, filename) -> str:
    return 'image/product/{title}/{filename}'.format(
        title=instance.title,
        filename=filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, null=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=get_avatar_path)

    def __str__(self):
        return self.user.username + '_profile'


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True, upload_to=get_cat_path)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories')

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    text = models.TextField(null=True, blank=True)
    rate = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)


class Specification(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100)
    free_delivery = models.BooleanField(default=False)
    images = models.ImageField(null=True, blank=True, upload_to=get_product_path)
    tags = models.ForeignKey(Tag, on_delete=models.PROTECT, related_name='tags', null=True, blank=True)
    reviews = models.ForeignKey(Review, on_delete=models.PROTECT, related_name='reviews', null=True, blank=True)
    rating = models.FloatField(default=0)
    full_description = models.TextField(null=True, blank=True)
    specifications = models.ManyToManyField(Specification, related_name='specifications', null=True, blank=True)

    def description(self):
        if len(str(self.full_description)) > 50:
            return str(self.full_description)[:50] + '...'
        return self.full_description


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sale_price = models.FloatField(default=0)
    dateFrom = models.DateField()
    dateTo = models.DateField()


class ProductOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='product')
    price = models.FloatField(default=0)
    count = models.IntegerField(default=0)


class Basket(models.Model):  # Возможно придется подумать
    products = models.ManyToManyField(ProductOrder, related_name='baskets')


class Order(models.Model):
    create_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    delivery_type = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=100)
    total_cost = models.FloatField()
    status = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    products = models.ManyToManyField(ProductOrder, related_name='orders')
