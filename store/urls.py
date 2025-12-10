from django.urls import path
from store import views   # <-- ЭТО ВАЖНО: импортируем views из store приложения

urlpatterns = [
    path('', views.home, name='home'),

    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),

    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase/<int:pk>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:pk>/', views.decrease_quantity, name='decrease_quantity'),

    path('checkout/', views.checkout, name='checkout'),

    path('profile/', views.profile, name='profile'),

    # Категории
    path('categories/', views.categories_list, name='categories'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
]
