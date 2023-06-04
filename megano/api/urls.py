from django.urls import path
from api import views

urlpatterns = [
    path('banners', views.banners),
    path('categories', views.CategoryView.as_view()),  # categories),
    path('catalog', views.CatalogView.as_view()),  # catalog),
    path('products/popular', views.productsPopular),
    path('products/limited', views.productsLimited),
    path('sales', views.sales),
    path('basket', views.basket),
    path('orders', views.orders),
    path('sign-in', views.signIn),
    path('sign-up', views.signUp),
    path('sign-out', views.signOut),
    path('product/<int:id>', views.ProductView.as_view()),  # product),
    path('product/<int:id>/reviews', views.ReviewView.as_view()),  # productReviews),
    path('tags', views.TagsView.as_view()),  # tags),
    path('profile', views.profile),
    path('profile/password', views.profilePassword),
    path('profile/avatar', views.avatar),
    path('order/<int:id>', views.order),
    path('payment/<int:id>', views.payment),
]
