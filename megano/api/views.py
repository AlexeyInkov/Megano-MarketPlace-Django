from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from random import randrange
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import GenericAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Category, Product, Tag, Review, Profile, Image
from .serializers import (
	CatalogItem,
	TagSerializer,
	ProductShort,
	ReviewSerializer,
	ProductFull, ProfileSerializer, ImageSerializer
)

User = get_user_model()

def banners(request):
	data = [
		{
			"id": "123",
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
					"alt": "any alt text",
				}
			],
			"tags": [
				"string"
			],
			"reviews": 5,
			"rating": 4.6
		},
	]
	return JsonResponse(data, safe=False)


class CategoryView(ListModelMixin, GenericAPIView):
	serializer_class = CatalogItem
	queryset = Category.objects.filter(parent=None).select_related('image')

	def get(self, request):
		return self.list(request)


class CatalogPagination(PageNumberPagination):
	page_size = 2
	page_query_param = 'currentPage'
	page_size_query_param = 'limit'
	max_page_size = 100


class CatalogView(ListModelMixin, GenericAPIView):  #TODO add filter category
	serializer_class = ProductShort
	pagination_class = CatalogPagination

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

# category = NaN

	def get_queryset(self):
		name = self.request.query_params.get('filter[name]')
		minPrice = self.request.query_params.get('filter[minPrice]')
		maxPrice = self.request.query_params.get('filter[maxPrice]')
		freeDelivery = self.request.query_params.get('filter[freeDelivery]')
		available = self.request.query_params.get('filter[available]')

		sort = self.request.query_params.get('sort')
		if self.request.query_params.get('sortType')  == 'dec':
			sort = '-' + sort

		category = self.request.query_params.get('category')
		print('category', category)
		queryset = Product.objects.prefetch_related('review').order_by(sort).all()
		queryset = queryset.filter(price__range=(int(minPrice), int(maxPrice))).order_by(sort).all()
		if name is not None:
			queryset = queryset.filter(title__icontains=name)
		if freeDelivery == 'true':
			queryset = queryset.filter(freeDelivery=True)
		if available == 'true':
			queryset = queryset.filter(count__gt=0)
		return queryset

	def get_last_page(self):
		lastPage = len(self.get_queryset()) // int(CatalogPagination.page_size)
		if len(self.get_queryset()) % int(CatalogPagination.page_size) > 0:
			lastPage += 1
		return lastPage

	def get(self, request):
		currentPage = int(self.request.query_params.get('currentPage'))
		lastPage = len(self.get_queryset()) / int(CatalogPagination.page_size)
		return JsonResponse(
			{
				"items": self.list(request).data['results'],
				"currentPage": currentPage,
				"lastPage": self.get_last_page()
			}
		)


class ProductPopularView(ListModelMixin, GenericAPIView):
	queryset = Product.objects.order_by('-rating').all()[:8]
	serializer_class = ProductShort

	def get(self, request):
		return self.list(request)


class ProductLimitedView(ListModelMixin, GenericAPIView):
	queryset = Product.objects.filter(limited_edition=True).all()[:16]
	serializer_class = ProductShort

	def get(self, request):
		return self.list(request)


def sales(request):
	data = {
		'items': [
			{
				"id": 123,
				"price": 500.67,
				"salePrice": 200.67,
				"dateFrom": "05-08",
				"dateTo": "05-20",
				"title": "video card",
				"images": [
						{
							"src": "https://proprikol.ru/wp-content/uploads/2020/12/kartinki-ryabchiki-14.jpg",
							"alt": "hello alt",
						}
				 ],
			}
		],
		'currentPage': randrange(1, 4),
		'lastPage': 3,
	}
	return JsonResponse(data)


def basket(request):
	if request.method == "GET":
		print('[GET] /api/basket/')
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
			},
			{
				"id": 124,
				"category": 55,
				"price": 201.675,
				"count": 5,
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

	elif (request.method == "POST"):
		body = json.loads(request.body)
		id = body['id']
		count = body['count']
		print('[POST] /api/basket/   |   id: {id}, count: {count}'.format(id=id, count=count))
		data = [
			{
				"id": id,
				"category": 55,
				"price": 500.67,
				"count": 13,
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

	elif (request.method == "DELETE"):
		body = json.loads(request.body)
		id = body['id']
		print('[DELETE] /api/basket/')
		data = [
			{
			"id": id,
			"category": 55,
			"price": 500.67,
			"count": 11,
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
	serializer_class = ProductFull
	queryset = Product.objects.all()
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
		product.rating = product.get_rating
		product.reviews = product.get_reviews
		product.save()
		return response


class ProfileView(RetrieveAPIView):
	serializer_class = ProfileSerializer
	queryset = Profile.objects.select_related('user')

	def get_object(self):
		return self.request.user.profile

	def get(self, request, *args, **kwargs):
		return self.retrieve(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		request.data['user'] = request.user.id
	# 	request.data['avatar'] = {}
	# 	request.data['avatar']['src'] = request.user.profile.avatar.src
		return Response(request, *args, **kwargs)


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



class AvatarView(CreateAPIView):
	serializer_class = ImageSerializer
	queryset = Image.objects.all()

	def get_object(self):
		return self.request.user.profile.avatar

	def post(self, request, *args, **kwargs):
		instance = self.get_object()
		request.data['src'] = request.FILES['avatar']
		request.data['alt'] = request.user.username
		serializer = self.serializer_class(instance, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return JsonResponse(serializer.data)



