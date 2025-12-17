from django.urls import path
from store import views

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
    path('categories/', views.categories_list, name='categories'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:pk>/payment/', views.payment_page, name='payment'),
    path('order/<int:pk>/payment/success/', views.payment_success, name='payment_success'),
    path('orders/', views.orders_list, name='orders'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('delivery/', views.delivery, name='delivery'),
    path('payment-info/', views.payment_info, name='payment_info'),
    path('warranty/', views.warranty, name='warranty'),
    path('help/', views.help_page, name='help'),
]
