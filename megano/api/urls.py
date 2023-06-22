from django.urls import path
from api import views

urlpatterns = [
# PROFILE
    path('profile', views.ProfileView.as_view()),  # DONE
    path('profile/password', views.ChangePasswordView.as_view()),  # DONE
    path('profile/avatar', views.AvatarView.as_view()),  # DONE

# AUTH
    path('sign-in', views.signIn, name='login'),  # DONE
    path('sign-up', views.RegisterView.as_view()),  # DONE
    path('sign-out', views.log_out),  # DONE

# SHOP
#   catalog
    path('banners', views.BannersView.as_view()),  # DONE случайный товар
    path('categories', views.CategoryView.as_view()),  # DONE
    path('catalog', views.CatalogView.as_view()),  # DONE
    path('products/popular', views.ProductPopularView.as_view()),  # DONE
    path('products/limited', views.ProductLimitedView.as_view()),  # DONE
    path('sales', views.SalesView.as_view()),  # DONE
#   product
    path('product/<int:id>', views.ProductView.as_view()),  # DONE
    path('product/<int:id>/reviews', views.ReviewView.as_view()),  # DONE
    path('tags', views.TagsView.as_view()),  # DONE

# BASKET
    path('basket', views.BasketView.as_view()),  # DONE

# ORDER
    path('orders', views.OrdersListCreateView.as_view()),  #
    path('order/<int:id>', views.OrderUpdateView.as_view()),  #
    path('payment/<int:id>', views.PaymentView.as_view()),  #


]
