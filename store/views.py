from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .models import Product, Order, OrderItem, Category


def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    q = request.GET.get("q")
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    sort = request.GET.get("sort", "new")
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "name_asc":
        products = products.order_by("name")
    elif sort == "name_desc":
        products = products.order_by("-name")
    else:
        products = products.order_by("-id")

    min_price = request.GET.get("min")
    max_price = request.GET.get("max")
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    paginator = Paginator(products, 8)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "store/home.html", {
        "page_obj": page_obj,
        "categories": categories,
        "sort": sort,
        "min_price": min_price,
        "max_price": max_price,
        "q": q,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "store/product_detail.html", {"product": product})


def add_to_cart(request, pk):
    cart = request.session.get("cart", {})
    quantity = int(request.POST.get("quantity", 1))
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


@login_required
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("cart")

    products = []
    total = 0

    for key, quantity in cart.items():
        product = Product.objects.get(id=key)
        product.quantity = quantity
        product.total_price = product.price * quantity
        total += product.total_price
        products.append(product)

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            phone=request.POST.get("phone"),
            delivery_type=request.POST.get("delivery_type"),
            address=request.POST.get("address", ""),
            total_price=total,
        )

        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=product.quantity,
                price=product.price,
            )

        request.session["cart"] = {}
        return render(request, "store/success.html", {"order": order})

    return render(request, "store/checkout.html", {
        "products": products,
        "total": total,
    })


@login_required
def profile(request):
    return render(request, "store/profile.html")


@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/order_list.html", {"orders": orders})


def categories_list(request):
    return render(request, "store/categories.html", {
        "categories": Category.objects.all()
    })


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
    if order.status not in ["Отменён", "Доставлен"]:
        order.status = "Отменён"
        order.save()
    return redirect("order_detail", pk=pk)


@login_required
def payment_page(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == "POST":
        order.status = "Оплачено"
        order.save()
        return redirect("payment_success", pk=order.id)
    return render(request, "store/payment.html", {"order": order})


@login_required
def payment_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "store/payment_success.html", {"order": order})


@login_required
def profile_edit(request):
    if request.method == "POST":
        request.user.username = request.POST.get("username")
        request.user.email = request.POST.get("email")
        request.user.save()
        return redirect("profile")
    return render(request, "store/profile_edit.html")


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("profile")
    return render(request, "store/change_password.html", {"form": form})


def delivery(request):
    return render(request, "store/delivery.html")


def payment_info(request):
    return render(request, "store/payment_info.html")


def warranty(request):
    return render(request, "store/warranty.html")


def help_page(request):
    return render(request, "store/help.html")
