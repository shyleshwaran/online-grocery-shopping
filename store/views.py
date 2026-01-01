from django.shortcuts import render, redirect, get_object_or_404
from.models import Product, Category, Cart, CartItem, Order, OrderItem
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required 
from .forms import SignUpForm, CheckoutForm


# Create your views here.

User = get_user_model()

def home(request):
    categories = Category.objects.all() if 'Category' in globals() else []
    products = Product.objects.all() if 'Product' in globals() else []
    return render(request, 'store/home.html', {
        'categories': categories,
        'products': products
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.product_set.filter(available=True)
    return render(request, 'store/category.html', {'category': category, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {'product': product})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. You're logged in.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'store/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def _get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = _get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Added {product.name} to cart")
    return redirect('cart')


@login_required
def cart_view(request):
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related('product').all()
    total = cart.total_price()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items, 'total': total})


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Item removed.")
    return redirect('cart')


@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        if qty < 1:
            item.delete()
        else:
            item.quantity = qty
            item.save()
    return redirect('cart')


@login_required
def checkout(request):
    cart = _get_or_create_cart(request.user)
    if not cart.items.exists():
        messages.info(request, "Your cart is empty")
        return redirect('home')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = cart.total_price()
            order.save()
            # move items
            for ci in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=ci.product,
                    price=ci.product.price,
                    quantity=ci.quantity,
                   
                )
            # clear cart
            cart.items.all().delete()
            messages.success(request, f"Order {order.id} placed successfully!")
            return redirect('order_detail')
           

    else:
        form = CheckoutForm(initial={'full_name': request.user.username})
    return render(request, 'store/checkout.html', {'form': form, 'cart': cart, 'total': cart.total_price()})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    for order in orders:
        # Attach items
        order.items_list = order.orderitem_set.all()

        # Calculate total if missing
        total = 0
        for item in order.items_list:
            total += item.price * item.quantity

        order.total = total

    return render(request, 'store/order_list.html', {'orders': orders})

@login_required
def order_detail(request):
    latest_order = Order.objects.filter(user=request.user).order_by('-id').first()

    if not latest_order:
        return render(request, 'store/order_detail.html', {'order': None})

    items = OrderItem.objects.filter(order=latest_order)

    return render(request, 'store/order_detail.html', {
        'order': latest_order,
        'items': items,
    })


