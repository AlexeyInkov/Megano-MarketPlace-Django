from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Category, Product, Tag, Image, Sale, Review, Profile, Specification


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['src', 'alt']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = 'id', 'name'


class ProfileSerializer(serializers.ModelSerializer):
    avatar = ImageSerializer(many=False, required=False, read_only=True)

    class Meta:
        model = Profile
        fields = 'fullName', 'email', 'phone', 'avatar'

    def update(self, instance, validated_data):
        pass



# Order


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['name', 'value']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['author', 'text', 'rate', 'date']


class ProductFull(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)
    reviews = ReviewSerializer(many=True, required=False)
    specifications = SpecificationSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'fullDescription',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'specifications',
            'rating'
        ]


class SaleItem(serializers.ModelSerializer):
    image = ImageSerializer(many=False, required=False)

    class Meta:
        model = Sale
        fields = [
            'id',
            'price',
            'salePrice',
            'dateFrom',
            'dateTo',
            'title',
        ]


class ProductShort(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'rating'
        ]


class Sales(serializers.ModelSerializer):
    items = SaleItem(many=True)

    class Meta:
        fields = 'items'


class Products(serializers.ModelSerializer):
    items = ProductShort(many=True)

    class Meta:
        fields = 'items'


class CatalogItem(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = 'id', 'title', 'image', 'subcategories'
        depth = 2


#  пока непонятно зачем
class CatalogItems(serializers.Serializer):
    items = CatalogItem()
