import json
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api.services.basket import Basket
from .models import (
    Category,
    Product,
    Tag,
    Review,
    Profile,
    Sale,
    Order,
    OrderProduct,
    Payment,
    StatusOrder
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

    def post(self, request):
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
        body = json.loads(request.body)
        username = body['username']
        password = body['password']
        basket = Basket(request)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            order = Order.objects.filter(user=user, status=StatusOrder.objects.get(id=1)).first()
            if not order:
                order = Order.objects.create(user=request.user, status=StatusOrder.objects.get(id=1)).save()
                basket.copy_to_order(order)
            else:
                basket.merge(user, order)

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)


class RegisterView(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        data_ = request.data.keys()
        for data in data_:
            data = json.loads(data)
        """Преобразую странный формат данных запроса"""
        user = User.objects.create(username=data['username'])
        user.set_password(data['password'])
        user.save()
        Profile.objects.create(user=user, fullName=data['name'])
        username = data['username']
        password = data['password']
        basket = Basket(request)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            order = Order.objects.create(user=user, status=StatusOrder.objects.get(id=1)).save()
            basket.copy_to_order(order)
            login(request, user)
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
        basket.change(user=request.user, product=product, count=count)
        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user, status=StatusOrder.objects.get(id=1)).get()
            if not order:
                order = Order.objects.create(user=request.user, status=StatusOrder.objects.get(id=1)).save()
                basket.copy_to_order(order)
        serializer = ProductShortSerializer(
            instance=product,
            data=request.session['basket'][str(product.id)],
            partial=True
        )
        if serializer.is_valid():
            return JsonResponse(serializer.data)

    def delete(self, request):
        basket = Basket(request)
        product = Product.objects.get(id=request.data['id'])
        count = - int(request.data['count'])
        price = product.price
        basket.change(user=request.user, product=product, count=count)
        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user, status=StatusOrder.objects.get(id=1)).get()
            if not order:
                order = Order.objects.create(user=request.user, status=StatusOrder.objects.get(id=1)).save()
                basket.copy_to_order(order)
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
    permission_classes = [IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        orders = (
            Order.objects.
            select_related('status_order').
            prefetch_related('order_products').
            filter(user=self.request.user, status__in=[2, 3])
        )
        data_orders = []
        for order in orders:
            order_products = order.get_products(order)
            data_products = []
            for order_product in order_products:
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
                    data_products.append(serialised.data)
            serialised = OrderSerializer(order, data={'products': data_products}, partial=True)
            if serialised.is_valid():
                data_orders.append(serialised.data)
        return JsonResponse(data_orders, safe=False)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user, status=StatusOrder.objects.get(id=1)).get()
            return JsonResponse({"orderId": order.id})
        return reverse_lazy('api:login')


class OrderUpdateView(GenericAPIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request, id):
        order = Order.objects.get(id=id)
        products = []
        for order_product in OrderProduct.objects.filter(order=order):
            product = Product.objects.get(id=order_product.product_id)
            data = {
                'count': order_product.count,
                'price': order_product.price
            }
            serialised = ProductShortSerializer(
                product,
                data=data,
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
            "status": order.status.status,
            "city": order.city,
            "address": order.address,
            "products": products
        }
        return JsonResponse(data)

    def post(self, request, id):
        request.data['id'] = request.data['orderId']
        order = Order.objects.get(id=request.data['id'])
        order.status = 2
        serialized = OrderSerializer(order, data=request.data, partial=True)
        if serialized.is_valid():
            serialized.save()
            Basket(request).clear()
            return JsonResponse({"orderId": request.data['id']})


class PaymentView(CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def get(self, request, id):
        order = Order.objects.get(id=id)
        if order.payment is None:
            return HttpResponse(status=200)
        if order.status == 3:
            return redirect("/history-order/")
        return HttpResponse(status=200)

    def post(self, request, id):
        order = Order.objects.get(id=id)
        if order.payment is None:
            value = request.data['number']
            if value.isdigit() and len(value) == 8 and int(value) % 2 == 0 and value[7] != '0':
                request.data['order'] = id
                request.data['value'] = value
                request.data['error'] = 'нет'
                order.status = 3
                order.save()
                return self.create(request)
            order.status = StatusOrder.objects.get(id=4)
            order.save()
        return HttpResponse(status=200)
