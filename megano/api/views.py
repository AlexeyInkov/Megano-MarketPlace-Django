from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from random import randrange
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.generics import GenericAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

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


# class CatalogPagination(PageNumberPagination):
# 	page_size = 10
# 	page_size_query_param = 'limit'
# 	page_query_param = 'page'
# 	max_page_size = 100


class CatalogView(ListModelMixin, GenericAPIView):
	serializer_class = ProductShort

	#pagination_class = CatalogPagination
	queryset = Product.objects.all()
	# def get_queryset(self):  # TODO сделать фильтрацию
	# 	queryset = Product.objects.all()
	# 	# book_name = self.request.query_params.get('name')
	# 	# author_name = self.request.query_params.get('author')
	# 	# page = self.request.query_params.get('page')
	# 	# page_up = self.request.query_params.get('page_up')
	# 	# page_down = self.request.query_params.get('page_down')
	# 	# if author_name and book_name:
	# 	# 	author_id = Author.objects.get(name=author_name)
	# 	# 	queryset = queryset.filter(name=book_name, author=author_id)
	# 	# elif page:
	# 	# 	queryset = queryset.filter(count_page=page)
	# 	# elif page_up:
	# 	# 	queryset = queryset.filter(count_page__gt=int(page_up))
	# 	# elif page_down:
	# 	# 	queryset = queryset.filter(count_page__lt=page_down)
	# 	return queryset

	def get(self, request):
		return JsonResponse(
			{
				"items": self.list(request).data,
				"currentPage": 1,
				"lastPage": 3
			}
		)


def productsPopular(request):
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

def productsLimited(request):
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

# def product(request, id):
# 	data = {
# 		"id": 123,
# 		"category": 55,
# 		"price": 500.67,
# 		"count": 12,
# 		"date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
# 		"title": "video card",
# 		"description": "description of the product",
# 		"fullDescription": "full description of the product",
# 		"freeDelivery": True,
# 		"images": [
# 				{
# 					"src": "https://proprikol.ru/wp-content/uploads/2020/12/kartinki-ryabchiki-14.jpg",
# 					"alt": "hello alt",
# 				}
# 		 ],
# 		 "tags": [
# 				{
# 					"id": 0,
# 					"name": "Hello world"
# 				}
# 		 ],
# 		"reviews": [
# 			{
# 				"author": "Annoying Orange",
# 				"email": "no-reply@mail.ru",
# 				"text": "rewrewrwerewrwerwerewrwerwer",
# 				"rate": 4,
# 				"date": "2023-05-05 12:12"
# 			}
# 		],
# 		"specifications": [
# 			{
# 				"name": "Size",
# 				"value": "XL"
# 			}
# 		],
# 		"rating": 4.6
# 	}
# 	return JsonResponse(data)


class ProductView(RetrieveAPIView):
	serializer_class = ProductFull
	queryset = Product.objects.all()
	lookup_field = 'id'


class TagsView(ListModelMixin, GenericAPIView):
	serializer_class = TagSerializer
	queryset = Tag.objects.all()

	def get(self, request):
		return self.list(request)


# def productReviews(request, id):
# 	data = [
#     {
#       "author": "Annoying Orange",
#       "email": "no-reply@mail.ru",
#       "text": "rewrewrwerewrwerwerewrwerwer",
#       "rate": 4,
#       "date": "2023-05-05 12:12"
#     },
#     {
#       "author": "2Annoying Orange",
#       "email": "no-reply@mail.ru",
#       "text": "rewrewrwerewrwerwerewrwerwer",
#       "rate": 5,
#       "date": "2023-05-05 12:12"
#     },
# 	]
# 	return JsonResponse(data, safe=False)


class ReviewView(CreateAPIView):
	serializer_class = ReviewSerializer
	queryset = Review.objects.select_related('product')


	def post(self, request, *args, **kwargs):
		request.data['product'] = kwargs['id']
		return self.create(request, *args, **kwargs)


class ProfileView(RetrieveAPIView):
	serializer_class = ProfileSerializer
	queryset = Profile.objects.select_related('user')

	def get_object(self):
		return self.request.user.profile

	def get(self, request, *args, **kwargs):
		return self.retrieve(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		instance = self.get_object()
		request.data['user'] = request.user.id
		request.data['pk'] = instance.pk
		print(request.data)
		serializer = self.serializer_class(instance, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return JsonResponse(serializer.data)



	# if(request.method == 'GET'):
	# 	data = {
	# 		"fullName": "Annoying Orange",
	# 		"email": "no-reply@mail.ru",
	# 		"phone": "88002000600",
	# 		"avatar": {
	# 			"src": "https://proprikol.ru/wp-content/uploads/2020/12/kartinki-ryabchiki-14.jpg",
	# 			"alt": "hello alt",
	# 		}
	# 	}
	# 	return JsonResponse(data)
	#
	# elif(request.method == 'POST'):
	# 	data = {
	# 		"fullName": "Annoying Green",
	# 		"email": "no-reply@mail.ru",
	# 		"phone": "88002000600",
	# 		"avatar": {
	# 			"src": "https://proprikol.ru/wp-content/uploads/2020/12/kartinki-ryabchiki-14.jpg",
	# 			"alt": "hello alt",
	# 		}
	# 	}
	# 	return JsonResponse(data)
	#
	# return HttpResponse(status=500)

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


# def avatar(request):
# 	if request.method == "POST":
# 		instance = Image.objects.get(pk=request.user.profile.avatar)
# 		instance.src = request.FILES['avatar']
# 		instance.save()
# 		return JsonResponse(
# 			ImageSerializer(instance).data)


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



