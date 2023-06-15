"""
TODO
настроить разрешения
"""

import random

from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from random import randrange
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import GenericAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, ListAPIView, \
	UpdateAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .basket import Basket

from .models import (
	Category,
	Product,
	Tag,
	Review,
	Profile,
	Sale
)
from .serializers import (
	CatalogSerializer,
	TagSerializer,
	ProductShortSerializer,
	ReviewSerializer,
	ProductFullSerializer,
	ProfileSerializer,
	ImageSerializer,
	SaleSerializer,
	AvatarSerializer
)

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


class Pagination(PageNumberPagination):
	page_size = 20
	page_query_param = 'currentPage'
	page_size_query_param = 'limit'
	max_page_size = 100


class CatalogView(ListModelMixin, GenericAPIView):
	serializer_class = ProductShortSerializer
	pagination_class = Pagination

	def get_order(self):
		sort = self.request.query_params.get('sort')
		if self.request.query_params.get('sortType') == 'inc':
			return sort
		return '-' + sort

	filter_backends = [
		OrderingFilter
	]
	ordering_fields = [
		get_order,
	]

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
		print(queryset)
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
	# serializer_class = BasketSerializer
	# queryset = (
	# 	Basket.objects
	# 	.select_related('product')
	# 	.select_related('user')
	# 	# .filter(user=get_user)
	# )

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
		basket.change(product=product, count=request.data['count'])
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
		count = - request.data['count']
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


def orders(request):
	if (request.method == "POST"):
		data = [
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
						"alt": "hello alt",
					}
			 ],
			 "tags": [
					{
						"id": 0,
						"name": "Hello world"
					}
			 ],
				"reviews": 5,
				"rating": 4.6
			}
		]
		return JsonResponse(data, safe=False)

def signIn(request):
	if request.method == "POST":
		body = json.loads(request.body)
		username = body['username']
		password = body['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return HttpResponse(status=200)
		else:
			return HttpResponse(status=500)


def signUp(request):
	user = User.objects.create_user("mir232", "lennon@thebeatles.com", "pass232")
	user.save()
	return HttpResponse(status=200)


def signOut(request):
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



def profilePassword(request):
	return HttpResponse(status=200)

def orders(request):
	if(request.method == 'GET'):
		data = [
			{
        "id": 123,
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
          }
        ]
      },
			{
        "id": 123,
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
          }
        ]
      }
		]
		return JsonResponse(data, safe=False)

	elif(request.method == 'POST'):
		data = {
			"orderId": 123,
		}
		return JsonResponse(data)

	return HttpResponse(status=500)

def order(request, id):
	if(request.method == 'GET'):
		data = {
			"id": 123,
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
		data = { "orderId": 123 }
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



