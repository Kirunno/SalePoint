from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import random
import string
from .models import Product, Order, OrderItem, Category


# -------------------------------------------------------
# Главная страница (поиск, фильтры, категории, сортировка)
# -------------------------------------------------------

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()   # <-- в шаблоне используется!

    # --- ПОИСК ---
    q = request.GET.get("q")
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    # --- СОРТИРОВКА ---
    sort = request.GET.get("sort", "new")

    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "name_asc":
        products = products.order_by("name")
    elif sort == "name_desc":
        products = products.order_by("-name")
    else:  # new
        products = products.order_by("-id")

    # --- ФИЛЬТР ПО ЦЕНЕ ---
    min_price = request.GET.get("min")
    max_price = request.GET.get("max")

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # --- ФИЛЬТР ПО НАЛИЧИЮ ---
    in_stock = request.GET.get("stock")

    if in_stock == "yes":
        products = products.filter(is_available=True)
    elif in_stock == "no":
        products = products.filter(is_available=False)

    # --- ПАГИНАЦИЯ ---
    paginator = Paginator(products, 8)  # 8 товаров на странице
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "categories": categories,     # <-- обязательно для блока категорий
        "sort": sort,
        "min_price": min_price,
        "max_price": max_price,
        "stock": in_stock,
        "q": q,
    }

    return render(request, "store/home.html", context)




# -------------------------------------------------------
# Детальная страница товара
# -------------------------------------------------------
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "store/product_detail.html", {"product": product})


# -------------------------------------------------------
# Корзина — добавление, удаление, изменение количества
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

        request.session["cart"] = {}  # очистить корзину

        return render(request, "store/success.html", {"order": order})

    return render(request, "store/checkout.html")


# -------------------------------------------------------
# Профиль — история заказов
# -------------------------------------------------------
@login_required
def profile(request):
    status_filter = request.GET.get("status", "all")
    sort_order = request.GET.get("sort", "new")

    orders = Order.objects.filter(user=request.user)

    # Фильтр по статусу
    if status_filter != "all":
        orders = orders.filter(status=status_filter)

    # Сортировка
    if sort_order == "new":
        orders = orders.order_by("-created_at")
    else:
        orders = orders.order_by("created_at")

    return render(request, "store/profile.html", {
        "orders": orders,
        "status_filter": status_filter,
        "sort_order": sort_order,
    })



# -------------------------------------------------------
# Список категорий
# -------------------------------------------------------
def categories_list(request):
    categories = Category.objects.all()
    return render(request, "store/categories.html", {"categories": categories})


# -------------------------------------------------------
# Товары выбранной категории
# -------------------------------------------------------
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category)

    return render(request, "store/category_detail.html", {
        "category": category,
        "products": products,
    })
    

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    items = OrderItem.objects.filter(order=order)

    return render(request, "store/order_detail.html", {
        "order": order,
        "items": items
    })


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)

    # Разрешаем отменять только если заказ ещё не отправлен/не выполнен
    if order.status not in ["Отменён", "Доставлен"]:
        order.status = "Отменён"
        order.save()

    return redirect('order_detail', pk=pk)


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)

    # Нельзя отменить доставленный или уже отменённый заказ
    if order.status in ["Отменён", "Доставлен"]:
        return redirect("order_detail", pk=order.id)

    if request.method == "POST":
        order.status = "Отменён"
        order.save()
        return redirect("order_detail", pk=order.id)

    return redirect("order_detail", pk=order.id)


@login_required
@csrf_exempt
def payment_page(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)

    # Если заказ уже оплачен
    if order.status == "Оплачено":
        return redirect("order_detail", pk=order.id)

    # POST — имитация успешной оплаты
    if request.method == "POST":
        order.status = "Оплачено"
        order.save()
        return redirect("order_detail", pk=order.id)

    return render(request, "store/payment.html", {
        "order": order
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_list.html', {'orders': orders})


def payment_success(request, pk):
    order = get_object_or_404(Order, id=pk)

    # Меняем статус заказа
    order.status = "Оплачено"
    order.save()

    return render(request, "store/payment_success.html", {"order": order})


@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders_list.html', {'orders': orders})


@login_required
def profile_edit(request):
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        user.username = username
        user.email = email
        user.save()

        return redirect("profile")

    return render(request, "store/profile_edit.html", {"user": user})



@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Чтобы не разлогинило
            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "store/change_password.html", {"form": form})


def delivery(request):
    return render(request, "store/delivery.html")

def payment_info(request):
    return render(request, "store/payment_info.html")

def warranty(request):
    return render(request, "store/warranty.html")



def generate_tracking_code():
    prefix = "KZ"
    number = "".join(random.choices(string.digits, k=9))
    suffix = "KZ"
    return f"{prefix}{number}{suffix}"





