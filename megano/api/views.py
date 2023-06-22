"""
TODO
настроить разрешения
"""

import random
from decimal import *

from django.contrib.auth.models import User
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
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from api.services.basket import BasketAnonim, BasketService

from .models import (
    Category,
    Product,
    Tag,
    Review,
    Profile,
    Sale,
    Order,
    OrderProduct,
    Payment
)
from .serializers import (
    CatalogSerializer,
    TagSerializer,
    ProductShortSerializer,
    ReviewSerializer,
    ProductFullSerializer,
    ProfileSerializer,
    SaleSerializer,
    AvatarSerializer,
    OrderSerializer,
    OrderProductSerializer,
    ChangePasswordSerializer,
    UserSerializer,
    PaymentSerializer
)
from .services.shop import Pagination


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.select_related('user')
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        return self.request.user.profile

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated, IsAdminUser)

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


class AvatarView(UpdateModelMixin, GenericAPIView):
    serializer_class = AvatarSerializer
    queryset = Profile.objects.select_related("avatar")
    permission_classes = [IsAuthenticated, IsAdminUser]

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


def signIn(request):
    if request.method == "POST":
        old_basket = BasketAnonim(request)
        body = json.loads(request.body)
        username = body['username']
        password = body['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            new_basket = BasketService(request)
            new_basket.merge_baskets(old_basket)
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
        old_basket = BasketAnonim(request)
        user = User.objects.create(username=data['username'])
        user.set_password(data['password'])
        user.save()
        profile = Profile.objects.create(user=user, fullName=data['name'])
        username = data['username']
        password = data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            new_basket = BasketService(request)
            new_basket.merge_baskets(old_basket)
            return HttpResponse(status=200)
        return HttpResponse(status=500)


def log_out(request):
    logout(request)
    return HttpResponse(status=200)


#   CATALOG


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


class BannersView(ListAPIView):
    serializer_class = ProductShortSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        rnd = random.randint(1, len(queryset))
        return queryset[(rnd - 1):rnd]


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


#   PRODUCT


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
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, *args, **kwargs):
        request.data['product'] = kwargs['id']
        response = self.create(request, *args, **kwargs)
        product = Product.objects.get(id=kwargs['id'])
        product.save()
        return response


#   BASKET


class BasketView(GenericAPIView):
    def get(self, request):
        basket = BasketService(request)
        print('--------------basketview', type(basket))
        print('-------------', isinstance(basket, Order))
        if isinstance(basket, Order,):
            data = []
            for order_product in basket.get_products():
                serializer = ProductShortSerializer(instance=order_product.product, data={'count': order_product.count})
                data.append(serializer.data)
        else:
            data = []
            for item in basket.get_goods():
                product = ProductShortSerializer(instance=item['product']).data
                product['count'] = item['count']
                product['price'] = item['price']
                data.append(product)
        return JsonResponse(data, safe=False)

    def post(self, request):
        basket = BasketService(request)
        product = Product.objects.get(id=request.data['id'])
        count = int(request.data['count'])
        price = product.price
        basket.add_to_basket(product=product, count=count, price=price)
        serializer = ProductShortSerializer(
            instance=product,
            data=request.session['basket'][str(product.id)],
            partial=True
        )
        if serializer.is_valid():
            return JsonResponse(serializer.data)

    def delete(self, request):
        product = Product.objects.get(id=request.data['id'])
        count = - int(request.data['count'])
        price = product.price
        BasketService.add_to_basket(product=product, count=count, price=price)
        data = request.session['basket'].get(str(product.id), None)
        if data:
            serializer = ProductShortSerializer(
                instance=product,
                data=data,
                partial=True
            )
            if serializer.is_valid():
                return JsonResponse(serializer.data)
        return JsonResponse({})


#   ORDER


class OrdersListCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        orders = Order.objects.prefetch_related('products').filter(user=self.request.user)
        data_orders = []
        for order in orders:
            print(order.products)


        #     order_products = OrderProduct.objects.filter(order=order)
        #     data_products = []
        #     print(order_products)
        #     for order_product in order_products:
        #         print(order_product.product_id)
        #         product = Product.objects.get(id=order_product.product_id)
        #         print(product)
        #         serialised = ProductShortSerializer(
        #             product,
        #             data={
        #                 'count': order_product.count,
        #                 'price': order_product.price
        #             },
        #             partial=True
        #         )
        #         if serialised.is_valid():
        #             data_products.append(serialised.data)
        #             print(serialised.data)
        #     print(order)
        #     serialised = OrderSerializer(order, data={})  # , data={'products': data_products}, partial=True)
        #     print(serialised)
        #     if serialised.is_valid():
        #         print('working')
        #         data_orders.append(serialised.data)
        #         print(serialised.data)
        return JsonResponse(data_orders, safe=False)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            order_serializer = OrderSerializer(
                data={
                    'user': request.user.pk,
                    'status': 'не подтвержден'
                },
                partial=True)
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
                basket = BasketAnonim(request)
                basket.clear()
            return JsonResponse({"orderId": order_serializer.data['id']})
        return reverse_lazy('api:login')  # Нашел login


class OrderUpdateView(GenericAPIView):
    def get(self, request, id):
        order = Order.objects.get(id=id)
        products = []
        for order_product in OrderProduct.objects.filter(order=order):
            product = Product.objects.get(id=order_product.product_id)
            serialised = ProductShortSerializer(
                product,
                data={
                    'count': order_product.count,
                    'price': order_product.price
                },
                partial=True
            )
            if serialised.is_valid():
                products.append(serialised.data)
        data = {
            "id": order.id,
            "createdAt": order.createdAt,
            "fullName": order.fullName or request.user.profile.fullName,
            "email": order.email or request.user.profile.email,
            "phone": order.phone or request.user.profile.phone,
            "deliveryType": order.deliveryType,
            "paymentType": order.paymentType,
            "totalCost": order.totalCost,
            "status": order.status,
            "city": order.city,
            "address": order.address,
            "products": products
        }
        return JsonResponse(data)

    def post(self, request, id):
        request.data['id'] = request.data['orderId']
        order = Order.objects.get(id=request.data['id'])
        serialized = OrderSerializer(order, data=request.data, partial=True)
        if serialized.is_valid():
            serialized.save()
        return JsonResponse({"orderId": request.data['id']})


class PaymentView(CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def post(self, request, id):
        order = Order.objects.get(id=id)
        value: str = request.data['number']
        if value.isdigit() and len(value) == 8 and int(value) % 2 == 0 and value[7] != '0':
            print('yes')
            request.data['order'] = id
            print(order.payment)
            if order.payment is None:
                return self.create(request)
            payment = Payment.objects.get(order=id)
            payment.number = value
            payment.save()
            order.status = 'Оплачено нe сразу'
            order.save()
            return HttpResponse(status=200)
        print('Ошибка оплаты')
        order.status = 'Ошибка оплаты'
        order.save()
        return HttpResponse(status=500)






