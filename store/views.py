from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Product, Order, OrderItem, Category


# -------------------------------------------------------
# Главная страница (поиск, фильтры, категории, сортировка)
# -------------------------------------------------------
def home(request):

    # Получаем параметры URL
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    sort = request.GET.get('sort')

    # Основной запрос
    products = Product.objects.all()
    categories = Category.objects.all()

    # Поиск по названию, описанию и категории
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Фильтр по категории
    if category_id:
        products = products.filter(category_id=category_id)

    # Фильтр по цене
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # Сортировка
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "new":
        products = products.order_by("-id")

    return render(request, "store/home.html", {
        "products": products,
        "categories": categories,
        "query": query,
    })


# -------------------------------------------------------
# Детальная страница товара
# -------------------------------------------------------
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "store/product_detail.html", {"product": product})


# -------------------------------------------------------
# Корзина — добавить, удалить, изменить количество
# -------------------------------------------------------
def add_to_cart(request, pk):
    cart = request.session.get("cart", {})

    quantity = int(request.POST.get("quantity", 1)) if request.method == "POST" else 1
    cart[str(pk)] = cart.get(str(pk), 0) + quantity

    request.session["cart"] = cart
    return redirect("cart")


def remove_from_cart(request, pk):
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    return redirect("cart")


def increase_quantity(request, pk):
    cart = request.session.get("cart", {})
    if str(pk) in cart:
        cart[str(pk)] += 1
    request.session["cart"] = cart
    return redirect("cart")


def decrease_quantity(request, pk):
    cart = request.session.get("cart", {})
    if str(pk) in cart:
        if cart[str(pk)] > 1:
            cart[str(pk)] -= 1
        else:
            del cart[str(pk)]
    request.session["cart"] = cart
    return redirect("cart")


def cart(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for key, quantity in cart.items():
        product = Product.objects.get(id=key)
        product.quantity = quantity
        product.total_price = product.price * quantity
        total += product.total_price
        products.append(product)

    return render(request, "store/cart.html", {
        "products": products,
        "total": total,
    })


# -------------------------------------------------------
# Оформление заказа
# -------------------------------------------------------
@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart")

    if request.method == "POST":
        delivery_type = request.POST.get("delivery_type")
        address = request.POST.get("address", "")
        phone = request.POST.get("phone", "Не указан")

        order = Order.objects.create(
            user=request.user,
            phone=phone,
            delivery_type=delivery_type,
            address=address,
            total_price=0,
        )

        total = 0

        for key, quantity in cart.items():
            product = Product.objects.get(id=key)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )

            total += product.price * quantity

        order.total_price = total
        order.save()

        # очистить корзину
        request.session["cart"] = {}

        return render(request, "store/success.html", {"order": order})

    return render(request, "store/checkout.html")


# -------------------------------------------------------
# Профиль — история заказов
# -------------------------------------------------------
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/profile.html", {"orders": orders})


# -------------------------------------------------------
# Страница списка всех категорий
# -------------------------------------------------------
def categories_list(request):
    categories = Category.objects.all()
    return render(request, "store/categories.html", {"categories": categories})


# -------------------------------------------------------
# Страница товаров конкретной категории
# -------------------------------------------------------
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category)

    return render(request, "store/category_detail.html", {
        "category": category,
        "products": products,
    })
