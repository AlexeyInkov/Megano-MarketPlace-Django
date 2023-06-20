from _decimal import Decimal
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
    email = models.EmailField(max_length=50, null=True, blank=True, unique=True)
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
    images = models.ManyToManyField(Image, related_name='product', default=[])
    rating = models.FloatField(default=0)
    tags = models.ManyToManyField(Tag, related_name='product', default=[], blank=True)
    fullDescription = models.TextField(null=True, blank=True)
    specifications = models.ManyToManyField(Specification, related_name='product', default=[], blank=True)
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


class Order(models.Model):
    # DELIVERY_CHOICES = [
    #     ('reg', 'Regular'),
    #     ('exp', 'Express'),
    #     ('free', 'Free')
    # # ]
    # PAYMENT_CHOICES = [
    #     ('card', 'Bank Card'),
    #     ('cash', 'From random account')
    # ]

    createdAt = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    fullName = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    deliveryType = models.CharField(max_length=10, default='reg')  # , choices=DELIVERY_CHOICES)
    city = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    paymentType = models.CharField(max_length=20, default='online')  # ,choices=PAYMENT_CHOICES,)

    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=100)


    @property
    def totalCost(self) -> Decimal:
        """Метод получения общей стоимости товаров в заказе"""
        return sum(product.get_cost() for product in self.products.all()) + self.delivery_cost


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.count


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment')
    number = models.CharField(max_length=8)
    # month = models.CharField(max_length=2)
    # year = models.CharField(max_length=2)
    # code = models.CharField(max_length=3)
    # name = models.CharField(max_length=25)
    # error = models.CharField(max_length=20)
