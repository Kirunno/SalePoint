from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem


def home(request):
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'store/home.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


def add_to_cart(request, pk):
    cart = request.session.get('cart', {})

    quantity = int(request.POST.get('quantity', 1))

    if str(pk) in cart:
        cart[str(pk)] += quantity
    else:
        cart[str(pk)] = quantity

    request.session['cart'] = cart
    return redirect('cart')


def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
    request.session['cart'] = cart
    return redirect('cart')


def increase_quantity(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        cart[str(pk)] += 1
    request.session['cart'] = cart
    return redirect('cart')


def decrease_quantity(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        if cart[str(pk)] > 1:
            cart[str(pk)] -= 1
        else:
            del cart[str(pk)]
    request.session['cart'] = cart
    return redirect('cart')


def cart(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for key, quantity in cart.items():
        product = Product.objects.get(id=key)
        product.quantity = quantity
        product.total_price = product.price * quantity
        total += product.total_price
        products.append(product)

    return render(request, 'store/cart.html', {
        'products': products,
        'total': total
    })


@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    if request.method == 'POST':
        delivery_type = request.POST.get('delivery_type')
        address = request.POST.get('address', '')

        order = Order.objects.create(
            user=request.user,
            phone="Не указан",
            delivery_type=delivery_type,
            address=address,
            total_price=0
        )

        total = 0

        for key, quantity in cart.items():
            product = Product.objects.get(id=key)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

            total += product.price * quantity

        order.total_price = total
        order.save()

        request.session['cart'] = {}

        return render(request, 'store/success.html', {'order': order})

    return render(request, 'store/checkout.html')


@login_required
def profile(request):
    return render(request, 'store/profile.html')
