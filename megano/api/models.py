from django.contrib.auth.models import User
from django.db import models


class Image(models.Model):
    image = models.ImageField()


class Profile(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, null=True)
    avatar = models.ForeignKey(Image, on_delete=models.PROTECT, related_name='avatar')


class Subcategory(models.Model):
    title = models.CharField(max_length=100)
    image = models.ForeignKey(Image, on_delete=models.PROTECT, related_name='image_subcat')


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ForeignKey(Image, on_delete=models.PROTECT, related_name='image_cat')
    subcategories = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='subcategories')


class Tag(models.Model):
    name = models.CharField(max_length=100)


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    text = models.TextField(null=True)
    rate = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)


class Specification(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)





class Product(models.Model):
    category = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='category')
    price = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100)
    free_delivery = models.BooleanField(default=False)
    images = models.ForeignKey(Image, on_delete=models.PROTECT, related_name='images_prod')
    tags = models.ForeignKey(Tag, on_delete=models.PROTECT, related_name='tags')
    reviews = models.ForeignKey(Review, on_delete=models.PROTECT, related_name='reviews')
    rating = models.FloatField(default=0)
    full_description = models.TextField(null=True)
    specifications = models.ManyToManyField(Specification, related_name='specifications')

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


class Basket(models.Model):
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




