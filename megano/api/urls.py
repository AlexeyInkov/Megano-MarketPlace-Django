from django.urls import path
from api import views

urlpatterns = [
    path('banners', views.BannersView.as_view()),  # DONE случайный товар
    path('categories', views.CategoryView.as_view()),  #
    path('catalog', views.CatalogView.as_view()),  #
    path('products/popular', views.ProductPopularView.as_view()),  # DONE
    path('products/limited', views.ProductLimitedView.as_view()),  # DONE
    path('sales', views.SalesView.as_view()),  # DONE
    path('basket', views.BasketView.as_view()),  #
    path('orders', views.orders),
    path('sign-in', views.signIn),  # DONE
    path('sign-up', views.signUp),
    path('sign-out', views.signOut),  # DONE
    path('product/<int:id>', views.ProductView.as_view()),  # DONE
    path('product/<int:id>/reviews', views.ReviewView.as_view()),  # DONE
    path('tags', views.TagsView.as_view()),  # DONE
    path('profile', views.ProfileView.as_view()),  #
    path('profile/password', views.profilePassword),
    path('profile/avatar', views.AvatarView.as_view()),  # avatar), DONE
    path('order/<int:id>', views.order),
    path('payment/<int:id>', views.payment),
]
