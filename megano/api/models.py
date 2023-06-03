

from django.contrib.auth.models import User
from django.db import models


def get_image_path(instance, filename) -> str:
    return 'image/{alt}/{filename}'.format(
        alt=instance.alt,
        filename=filename)


class Image(models.Model):
    src = models.ImageField(upload_to=get_image_path)
    alt = models.CharField(max_length=50)

    def __str__(self):
        return self.alt


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, null=True)
    avatar = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True, related_name='avatar')

    def __str__(self):
        return self.user.username + '_profile'


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True, related_name='category')
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
    images = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True, related_name='product')
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
