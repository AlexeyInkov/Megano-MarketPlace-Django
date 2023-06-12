"""
TODO
настроить формат дат
"""

from django.contrib.auth.models import User
from django.db import models


def get_image_path(instance, filename) -> str:
    return 'image/{alt}/{filename}'.format(
        alt=instance.alt,
        filename=filename)


class Image(models.Model):
    src = models.ImageField(upload_to=get_image_path)
    alt = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.alt


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fullName = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
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


class Specification(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return ' = '.join([self.name, self.value])


class Product(models.Model):

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    freeDelivery = models.BooleanField(default=False)
    images = models.ManyToManyField(Image, related_name='products', default=[])
    rating = models.FloatField(default=0)
    tags = models.ManyToManyField(Tag, related_name='products', default=[], blank=True)
    fullDescription = models.TextField(null=True, blank=True)
    specifications = models.ManyToManyField(Specification, related_name='products', default=[], blank=True)
    sold = models.IntegerField(default=0)
    limited_edition = models.BooleanField(default=False)

    def description(self):
        if len(str(self.fullDescription)) > 50:
            return str(self.fullDescription)[:50] + '...'
        return self.fullDescription

    @property
    def get_rating(self):
        queryset = Review.objects.filter(product=self.pk)
        if len(queryset) == 0:
            return 0
        return sum(review.rate for review in queryset) / len(queryset)

    # def reviews(self):
    #     queryset = Review.objects.filter(product=self.pk)
    #     return len(queryset)

    def __call__(self, *args, **kwargs):
        self.rating = self.get_rating
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Review(models.Model):
    author = models.CharField(max_length=50, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    rate = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return self.product.title


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale')
    salePrice = models.FloatField(default=0)
    dateFrom = models.DateField()
    dateTo = models.DateField()


class Basket(models.Model):
    user = models.ForeignKey(Profile,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='basket')
    count = models.IntegerField(default=0)


class Order(models.Model):
    create_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    delivery_type = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=100)
    total_cost = models.FloatField()
    status = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    products = models.ManyToManyField(Product, related_name='orders')
