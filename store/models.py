from django.db import models
from django.conf import settings


# -----------------------
# КАТЕГОРИИ
# -----------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name


# -----------------------
# ТОВАРЫ
# -----------------------
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField()
    old_price = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# -----------------------
# КОРЗИНА
# -----------------------
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Корзина {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity


# -----------------------
# ЗАКАЗЫ
# -----------------------
class Order(models.Model):

    DELIVERY_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('delivery', 'Доставка'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('online', 'Онлайн-оплата'),
    ]

    # Основные данные
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)              # Имя клиента
    email = models.EmailField(blank=True)                            # Email клиента
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)

    # Характеристики заказа
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='online')

    total_price = models.IntegerField(default=0)

    status = models.CharField(max_length=50, default="Обрабатывается")  # Статус заказа
    admin_comment = models.TextField(blank=True)                        # Комментарий менеджера (на будущее)

    tracking_number = models.CharField(max_length=100, blank=True)      # Номер отслеживания

    promo_code = models.CharField(max_length=50, blank=True)            # Промокод
    discount_amount = models.IntegerField(default=0)                    # Размер скидки

    comment = models.TextField(blank=True)                              # Комментарий клиента

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)                    # Дата изменения

    def __str__(self):
        return f"Заказ #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
