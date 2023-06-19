"""
TODO
настроить разрешения
"""

import random
from decimal import *
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, ListAPIView, \
    ListCreateAPIView, UpdateAPIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.servises.basket import Basket

from .models import (
    Category,
    Product,
    Tag,
    Review,
    Profile,
    Sale, Order
)
from .serializers import (
    CatalogSerializer,
    TagSerializer,
    ProductShortSerializer,
    ReviewSerializer,
    ProductFullSerializer,
    ProfileSerializer,
    SaleSerializer,
    AvatarSerializer, OrderSerializer, OrderProductSerializer, ChangePasswordSerializer, UserSerializer
)
from .servises.shop import Pagination

User = get_user_model()


class BannersView(ListAPIView):
    serializer_class = ProductShortSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        rnd = random.randint(1, len(queryset))
        return queryset[(rnd - 1):rnd]


class CategoryView(ListModelMixin, GenericAPIView):
    serializer_class = CatalogSerializer
    queryset = Category.objects.filter(parent=None).select_related('image')

    def get(self, request):
        return self.list(request)


class CatalogView(ListModelMixin, GenericAPIView):
    serializer_class = ProductShortSerializer
    pagination_class = Pagination

    def get_queryset(self):
        name = self.request.query_params.get('filter[name]')
        minPrice = self.request.query_params.get('filter[minPrice]')
        maxPrice = self.request.query_params.get('filter[maxPrice]')
        freeDelivery = self.request.query_params.get('filter[freeDelivery]')
        available = self.request.query_params.get('filter[available]')
        category = self.request.query_params.get('category')

        sort = self.request.query_params.get('sort')
        if self.request.query_params.get('sortType') == 'dec':
            sort = '-' + sort

        queryset = (
            Product.objects
            .prefetch_related('images')
            .prefetch_related('tags')
            .prefetch_related('reviews')
            .order_by(sort)
        )

        queryset = queryset.filter(price__range=(int(minPrice), int(maxPrice))).order_by(sort).all()

        if category is not None:
            queryset = queryset.filter(category=category)
        if name is not None:
            queryset = queryset.filter(title__icontains=name)
        if freeDelivery == 'true':
            queryset = queryset.filter(freeDelivery=True)
        if available == 'true':
            queryset = queryset.filter(count__gt=0)
        return queryset

    def get_last_page(self):
        lastPage = len(self.get_queryset()) // int(Pagination.page_size)
        if len(self.get_queryset()) % int(Pagination.page_size) > 0:
            lastPage += 1
        return lastPage

    def get(self, request):
        return JsonResponse(
            {
                "items": self.list(request).data['results'],
                "currentPage": int(self.request.query_params.get('currentPage')),
                "lastPage": self.get_last_page()
            }
        )


class ProductPopularView(ListModelMixin, GenericAPIView):
    queryset = Product.objects.order_by('-rating').all()[:8]
    serializer_class = ProductShortSerializer

    def get(self, request):
        return self.list(request)


class ProductLimitedView(ListModelMixin, GenericAPIView):
    queryset = Product.objects.filter(limited_edition=True).all()[:16]
    serializer_class = ProductShortSerializer

    def get(self, request):
        return self.list(request)


class SalesView(ListModelMixin, GenericAPIView):
    serializer_class = SaleSerializer
    pagination_class = Pagination

    def get_queryset(self):
        queryset = (
            Sale.objects
            .select_related('product')
        )
        return queryset

    def get_last_page(self):
        lastPage = len(self.get_queryset()) // int(Pagination.page_size)
        if len(self.get_queryset()) % int(Pagination.page_size) > 0:
            lastPage += 1
        return lastPage

    def get(self, request):
        items = self.list(request).data['results']
        for item in items:
            item.update(item.pop('product'))

        return JsonResponse(
            {
                "items": items,
                "currentPage": int(self.request.query_params.get('currentPage')),
                "lastPage": self.get_last_page()
            }
        )


class BasketView(GenericAPIView):
    def get(self, request):
        basket = Basket(request)
        data = []
        for item in basket:
            product = ProductShortSerializer(instance=item['product']).data
            product['count'] = item['count']
            product['price'] = item['price']
            data.append(product)
        return JsonResponse(data, safe=False)

    def post(self, request):
        basket = Basket(request)
        product = Product.objects.get(id=request.data['id'])
        count = int(request.data['count'])
        basket.change(product=product, count=count)
        serializer = ProductShortSerializer(
            instance=product,
            data=request.session['basket'][str(product.id)],
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

    def delete(self, request):
        basket = Basket(request)
        product = Product.objects.get(id=request.data['id'])
        count = - int(request.data['count'])
        basket.change(product=product, count=count)
        data = request.session['basket'].get(str(product.id), None)
        if data:
            serializer = ProductShortSerializer(
                instance=product,
                data=data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
        return JsonResponse({})


# def orders(request):
# 	if (request.method == "POST"):
# 		data = [
# 			{
# 			"id": 16,
# 			"category": 55,
# 			"price": 500.67,
# 			"count": 12,
# 			"date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
# 			"title": "video card",
# 			"description": "description of the product",
# 			"freeDelivery": True,
# 			"images": [
# 					{
# 						"src": "https://proprikol.ru/wp-content/uploads/2020/12/kartinki-ryabchiki-14.jpg",
# 						"alt": "hello alt",
# 					}
# 			 ],
# 			 "tags": [
# 					{
# 						"id": 0,
# 						"name": "Hello world"
# 					}
# 			 ],
# 				"reviews": 5,
# 				"rating": 4.6
# 			}
# 		]
# 		return JsonResponse(data, safe=False)


def signIn(request):
    if request.method == "POST":
        old_basket = Basket(request)
        print('old-\n', old_basket)
        body = json.loads(request.body)
        username = body['username']
        password = body['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            new_basket = Basket(request)
            print('new -\n', new_basket)
            new_basket.merge_baskets(old_basket)
            print('2 curt -\n', old_basket, '\n', new_basket)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)


class RegisterView(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        data_ = request.data.keys()
        for data in data_:
            data = json.loads(data)
        """Преобразую странный формат данных запроса"""
        user = User.objects.create(username=data['username'])
        user.set_password(data['password'])
        user.save()
        profile = Profile.objects.create(user=user, fullName=data['name'])
        old_basket = Basket(request)
        username = data['username']
        password = data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            new_basket = Basket(request)
            new_basket.merge_baskets(old_basket)
            return HttpResponse(status=200)
        return HttpResponse(status=500)


def log_out(request):
    logout(request)
    return HttpResponse(status=200)


class ProductView(RetrieveAPIView):
    serializer_class = ProductFullSerializer
    queryset = (
        Product.objects
        .prefetch_related('tags')
        .prefetch_related('specifications')
        .prefetch_related('images')
        .prefetch_related('tags')
        .prefetch_related('reviews')
    )
    lookup_field = 'id'


class TagsView(ListModelMixin, GenericAPIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get(self, request):
        return self.list(request)


class ReviewView(CreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related('product')

    def post(self, request, *args, **kwargs):
        request.data['product'] = kwargs['id']
        response = self.create(request, *args, **kwargs)
        product = Product.objects.get(kwargs['id'])
        product.save()
        return response


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.select_related('user')

    def get_object(self):
        return self.request.user.profile

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("currentPassword")):
                return Response({"currentPassword": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("newPassword"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdersListCreateView(ListModelMixin, GenericAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            order_serializer = OrderSerializer(data={'user': request.user.pk}, partial=True)
            if order_serializer.is_valid():
                order_serializer.save()
            for product in request.data:
                data = {
                    'order': order_serializer.data['id'],
                    'product': product['id'],
                    'price': product['price'],
                    'count': product['count']
                }
                product_serializer = OrderProductSerializer(data=data)
                if product_serializer.is_valid():
                    product_serializer.save()
                basket = Basket(request)
                basket.clear()
            return JsonResponse({"orderId": order_serializer.data['id']})
        return redirect('/login/')


def order(request, id):
    if(request.method == 'GET'):
        data = {
            "id": 16,
            "createdAt": "2023-05-05 12:12",
            "fullName": "Annoying Orange",
            "email": "no-reply@mail.ru",
            "phone": "88002000600",
            "deliveryType": "free",
            "paymentType": "online",
            "totalCost": 567.8,
            "status": "accepted",
            "city": "Moscow",
            "address": "red square 1",
            "products": [
                {
                    "id": 123,
                    "category": 55,
                    "price": 500.67,
                    "count": 12,
                    "date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
                    "title": "video card",
                    "description": "description of the product",
                    "freeDelivery": True,
                    "images": [
                        {
                            "src": "https://proprikol.ru/wp-content/uploads/2020/12/kartinki-ryabchiki-14.jpg",
                            "alt": "Image alt string"
                        }
                    ],
                    "tags": [
                        {
                            "id": 12,
                            "name": "Gaming"
                        }
                    ],
                    "reviews": 5,
                    "rating": 4.6
                },
            ]
        }
        return JsonResponse(data)

    elif(request.method == 'POST'):
        data = { "orderId": 16 }
        return JsonResponse(data)

    return HttpResponse(status=500)

def payment(request, id):
    print('qweqwewqeqwe', id)
    return HttpResponse(status=200)


class AvatarView(UpdateModelMixin, GenericAPIView):
    serializer_class = AvatarSerializer
    queryset = Profile.objects.select_related("avatar")

    def get_object(self):
        return self.request.user.profile

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {"avatar": {
            "src": request.FILES["avatar"],
            "alt": request.user.username + "_avatar"
        }}
        serializer = AvatarSerializer(instance=instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)



