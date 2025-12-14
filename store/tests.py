from django.test import TestCase, Client
from django.urls import reverse, resolve, NoReverseMatch
from django.contrib.auth.models import User
from store.models import Product, Category, Order, OrderItem


class BaseTest(TestCase):
    def setUp(self):
        # user
        self.user = User.objects.create_user(username="test", password="1234")

        # category
        self.category = Category.objects.create(name="Смартфоны")

        # products
        self.product1 = Product.objects.create(
            category=self.category,
            name="iPhone 15",
            description="Test",
            price=1000,
            is_available=True
        )
        self.product2 = Product.objects.create(
            category=self.category,
            name="Samsung S25",
            description="Test2",
            price=1500,
            is_available=True
        )

        self.client = Client()


# -----------------------------
# HOME PAGE TESTS
# -----------------------------
class HomePageTests(BaseTest):

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_search_products(self):
        response = self.client.get(reverse("home"), {"q": "iPhone"})
        self.assertContains(response, "iPhone 15")

    def test_price_filter(self):
        response = self.client.get(reverse("home"), {"min": "1200"})
        self.assertContains(response, "Samsung S25")
        self.assertNotContains(response, "iPhone 15")

    def test_sorting(self):
        response = self.client.get(reverse("home"), {"sort": "price_desc"})
        self.assertContains(response, "Samsung S25")


# -----------------------------
# CART TESTS
# -----------------------------
class CartTests(BaseTest):

    def test_add_to_cart(self):
        response = self.client.post(reverse("add_to_cart", args=[self.product1.id]), {"quantity": 1})
        cart = self.client.session["cart"]
        self.assertIn(str(self.product1.id), cart)
        self.assertEqual(cart[str(self.product1.id)], 1)

    def test_increase_quantity(self):
        self.client.post(reverse("add_to_cart", args=[self.product1.id]))
        self.client.get(reverse("increase_quantity", args=[self.product1.id]))
        cart = self.client.session["cart"]
        self.assertEqual(cart[str(self.product1.id)], 2)

    def test_remove_from_cart(self):
        self.client.post(reverse("add_to_cart", args=[self.product1.id]))
        self.client.get(reverse("remove_from_cart", args=[self.product1.id]))
        cart = self.client.session["cart"]
        self.assertNotIn(str(self.product1.id), cart)


# -----------------------------
# CHECKOUT TESTS
# -----------------------------
class CheckoutTests(BaseTest):

    def test_checkout_requires_login(self):
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 302)

    def test_checkout_success(self):
        self.client.login(username="test", password="1234")

        # add to cart
        self.client.post(reverse("add_to_cart", args=[self.product1.id]), {"quantity": 2})

        response = self.client.post(reverse("checkout"), {
            "delivery_type": "delivery",
            "address": "Street 1",
            "phone": "1234567",
            "payment_method": "cash"
        })

        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.total_price, 2000)
        self.assertEqual(order.status, "Обрабатывается")


# -----------------------------
# ORDER TESTS
# -----------------------------
class OrderTests(BaseTest):

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            user=self.user,
            phone="123",
            delivery_type="delivery",
            total_price=2000,
            status="Обрабатывается"
        )
        OrderItem.objects.create(order=self.order, product=self.product1, quantity=2, price=1000)

    def test_order_detail_requires_login(self):
        url = reverse("order_detail", args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_order_detail_authorized(self):
        self.client.login(username="test", password="1234")
        url = reverse("order_detail", args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2000")

    def test_cancel_order(self):
        self.client.login(username="test", password="1234")
        url = reverse("cancel_order", args=[self.order.id])
        self.client.post(url)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "Отменён")

    def test_payment_success(self):
        self.client.login(username="test", password="1234")
        url = reverse("payment", args=[self.order.id])
        self.client.post(url)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "Оплачено")


# -----------------------------
# CATEGORY TESTS
# -----------------------------
class CategoryTests(BaseTest):

    def test_category_page(self):
        url = reverse("category_detail", args=[self.category.id])
        response = self.client.get(url)
        self.assertContains(response, "iPhone 15")
        self.assertContains(response, "Samsung S25")


# ------------------------------------------------------
# GLOBAL URL TEST — ПРОВЕРКА, ЧТО КАЖДЫЙ URL ЖИВОЙ
# ------------------------------------------------------
class UrlSmokeTests(BaseTest):

    def test_all_urls(self):
        """Проверяем, что основные маршруты доступны (200 или 302)."""

        urls = [
            "home",
            "cart",
            "categories",
            "orders",
            "profile",
            "checkout",
            "delivery",
            "payment_info",
            "warranty",
        ]

        for name in urls:
            try:
                url = reverse(name)
                response = self.client.get(url)
                self.assertIn(
                    response.status_code,
                    [200, 302],
                    f"URL {name} вернул ошибку {response.status_code}"
                )
            except NoReverseMatch:
                self.fail(f"URL name '{name}' отсутствует в urls.py")
