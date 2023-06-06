from django.urls import path
from api import views

urlpatterns = [
    path('banners', views.banners),
    path('categories', views.CategoryView.as_view()),  # categories), DONE
    path('catalog', views.CatalogView.as_view()),  # catalog), DONE?
    path('products/popular', views.ProductPopularView.as_view()),  # productsPopular),
    path('products/limited', views.ProductLimitedView.as_view()),  # productsLimited), DONE
    path('sales', views.sales),
    path('basket', views.basket),
    path('orders', views.orders),
    path('sign-in', views.signIn),
    path('sign-up', views.signUp),
    path('sign-out', views.signOut),
    path('product/<int:id>', views.ProductView.as_view()),  # product), DONE
    path('product/<int:id>/reviews', views.ReviewView.as_view()),  # productReviews), DONE
    path('tags', views.TagsView.as_view()),  # tags), DONE
    path('profile', views.ProfileView.as_view()),  # profile),
    path('profile/password', views.profilePassword),
    path('profile/avatar', views.AvatarView.as_view()),  # avatar), DONE
    path('order/<int:id>', views.order),
    path('payment/<int:id>', views.payment),
]
