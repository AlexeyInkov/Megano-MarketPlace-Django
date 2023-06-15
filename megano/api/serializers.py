"""
TODO
настроить формат дат
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Category,
    Product,
    Tag,
    Image,
    Sale,
    Review,
    Profile,
    Specification,
)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['src', 'alt']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = 'id', 'name'


class AvatarSerializer(serializers.ModelSerializer):
    avatar = ImageSerializer()

    class Meta:
        model = Profile
        fields = ['avatar']

    def update(self, instance, validated_data):
        avatar_data = validated_data.pop('avatar')
        avatar = Image.objects.create(**avatar_data)
        instance.avatar = avatar
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    avatar = ImageSerializer(read_only=True)


    class Meta:
        model = Profile
        fields = 'user', 'fullName', 'email', 'phone', 'avatar'
        read_only_fields =['user']

    def update(self, instance, validated_data):
        instance.fullName = validated_data.get('fullName', instance.fullName)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['name', 'value']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['author', 'text', 'rate', 'date', 'product']


class ProductFullSerializer(serializers.ModelSerializer):
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


class ProductSaleSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'price',
            'title',
            'images'
        ]


class SaleSerializer(serializers.ModelSerializer):
    product = ProductSaleSerializer()
    dateFrom = serializers.DateField(format='%m-%d')
    dateTo = serializers.DateField(format='%m-%d')

    class Meta:
        model = Sale
        fields = [
            'id',
            'salePrice',
            'dateFrom',
            'dateTo',
            'product',

        ]


class ProductShortSerializer(serializers.ModelSerializer):
    def get_reviews(self, instance):
        return len(Review.objects.filter(product=instance.pk))

    images = ImageSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)
    reviews = serializers.SerializerMethodField(source=get_reviews)

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


class CatalogSerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = Category
        fields = 'id', 'title', 'image', 'subcategories'
        depth = 2
