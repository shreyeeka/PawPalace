from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.conf import settings

import stripe
from products.models import Product
from .models import CartItem, Order, OrderItem
from .forms import CheckoutForm
from payments.models import Payment
from decimal import Decimal


@login_required
def add_to_cart(request, product_id):
    """Add product to cart."""
    if not request.user.is_customer():
        messages.error(request, 'Only customers can add items to cart.')
        return redirect('products:list')
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if not product.is_in_stock():
        messages.error(request, 'Product is out of stock.')
        return redirect('products:detail', slug=product.slug)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > product.stock:
            messages.error(request, f'Only {product.stock} items available in stock.')
            return redirect('products:detail', slug=product.slug)
        
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                cart_item.quantity = product.stock
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Item added to cart'})
        
        return redirect('orders:cart')
    
    return redirect('products:detail', slug=product.slug)


@login_required
def cart(request):
    """Shopping cart page."""
    if not request.user.is_customer():
        messages.error(request, 'Only customers can view cart.')
        return redirect('products:home')
    
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'orders/cart.html', context)


@login_required
def update_cart(request, item_id):
    """Update cart item quantity."""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
        elif quantity > cart_item.product.stock:
            messages.error(request, f'Only {cart_item.product.stock} items available in stock.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated.')
    
    return redirect('orders:cart')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('orders:cart')


@login_required
def buy_now(request, product_id):
    """Buy now - add to cart and redirect to checkout."""
    if not request.user.is_customer():
        messages.error(request, 'Only customers can purchase.')
        return redirect('products:list')
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if not product.is_in_stock():
        messages.error(request, 'Product is out of stock.')
        return redirect('products:detail', slug=product.slug)
    
    # Get quantity from POST or GET, default to 1
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
    else:
        quantity = int(request.GET.get('quantity', 1))
    
    if quantity < 1:
        quantity = 1
    if quantity > product.stock:
        messages.error(request, f'Only {product.stock} items available in stock.')
        return redirect('products:detail', slug=product.slug)
    
    # Clear existing cart and add this product
    CartItem.objects.filter(user=request.user).delete()
    CartItem.objects.create(
        user=request.user,
        product=product,
        quantity=quantity
    )
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('orders:checkout')


@login_required
def checkout(request):
    """Checkout page with payment method selection."""
    if not request.user.is_customer():
        messages.error(request, 'Only customers can checkout.')
        return redirect('products:home')
    
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('orders:cart')
    
    # Check stock availability
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f'{item.product.name} is out of stock.')
            return redirect('orders:cart')
    
    subtotal = sum(item.get_total_price() for item in cart_items)
    shipping_cost = Decimal('50.00') if subtotal < Decimal('500.00') else Decimal('0.00')
    total = subtotal + shipping_cost
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        payment_method = request.POST.get('payment_method', 'cod')
        
        if form.is_valid():
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    customer=request.user,
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    total=total,
                    shipping_name=form.cleaned_data['shipping_name'],
                    shipping_phone=form.cleaned_data['shipping_phone'],
                    shipping_address=form.cleaned_data['shipping_address'],
                    shipping_city=form.cleaned_data['shipping_city'],
                    shipping_state=form.cleaned_data['shipping_state'],
                    shipping_zip=form.cleaned_data['shipping_zip'],
                    notes=form.cleaned_data.get('notes', ''),
                )
                
                # Create order items and update stock
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        product_name=cart_item.product.name,
                        quantity=cart_item.quantity,
                        price=cart_item.product.get_final_price(),
                        total=cart_item.get_total_price(),
                    )
                    # Update product stock
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()
                
                # Create payment record
                from payments.models import Payment
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=total,
                )
                
                # Clear cart
                cart_items.delete()
                
                # Redirect based on payment method
                if payment_method == 'esewa':
                    return redirect('payments:esewa_payment', order_number=order.order_number)
                else:  # COD
                    payment.status = 'pending'
                    payment.save()
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, f'Order placed successfully! Order #: {order.order_number}')
                    return redirect('orders:order_success', order_number=order.order_number)
    else:
        # Pre-fill form with user data
        initial_data = {
            'shipping_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'shipping_phone': request.user.phone or '',
            'shipping_address': request.user.address or '',
            'shipping_city': request.user.city or '',
            'shipping_state': request.user.state or '',
            'shipping_zip': request.user.zip_code or '',
        }
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'currency': settings.STRIPE_CURRENCY,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@require_POST
def create_stripe_checkout(request):
    """Create order + Stripe Checkout Session, return session id for redirect."""
    if not request.user.is_customer():
        return JsonResponse({'error': 'Only customers can checkout.'}, status=403)

    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return JsonResponse({'error': 'Your cart is empty.'}, status=400)

    # Validate stock
    for item in cart_items:
        if item.quantity > item.product.stock:
            return JsonResponse({'error': f'{item.product.name} is out of stock.'}, status=400)

    subtotal = sum(item.get_total_price() for item in cart_items)
    shipping_cost = Decimal('50.00') if subtotal < Decimal('500.00') else Decimal('0.00')
    total = subtotal + shipping_cost

    form = CheckoutForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Please fix the form errors and try again.'}, status=400)

    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLIC_KEY:
        return JsonResponse({'error': 'Stripe keys are not configured.'}, status=500)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    with transaction.atomic():
        # Create order
        order = Order.objects.create(
            customer=request.user,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total,
            shipping_name=form.cleaned_data['shipping_name'],
            shipping_phone=form.cleaned_data['shipping_phone'],
            shipping_address=form.cleaned_data['shipping_address'],
            shipping_city=form.cleaned_data['shipping_city'],
            shipping_state=form.cleaned_data['shipping_state'],
            shipping_zip=form.cleaned_data['shipping_zip'],
            notes=form.cleaned_data.get('notes', ''),
        )

        # Order items and stock update
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.product.get_final_price(),
                total=cart_item.get_total_price(),
            )
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # Create payment placeholder
        payment = Payment.objects.create(
            order=order,
            payment_method='stripe',
            amount=total,
            status='processing',
        )

        # Create Stripe Checkout Session
        amount_int = int(total * 100)
        success_url = request.build_absolute_uri(
            reverse('payment_success') + f'?order_number={order.order_number}&session_id={{CHECKOUT_SESSION_ID}}'
        )
        cancel_url = request.build_absolute_uri(
            reverse('payment_cancel') + f'?order_number={order.order_number}'
        )

        try:
            session = stripe.checkout.Session.create(
                mode='payment',
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': settings.STRIPE_CURRENCY,
                        'product_data': {'name': 'PawPalace Order'},
                        'unit_amount': amount_int,
                    },
                    'quantity': 1,
                }],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={'order_number': order.order_number},
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        payment.transaction_id = session.id
        payment.save()
        cart_items.delete()

    return JsonResponse({'id': session.id})


@login_required
def order_detail(request, order_number):
    """Order detail page."""
    order = get_object_or_404(Order, order_number=order_number)
    
    if not (request.user == order.customer or request.user.is_admin() or request.user.is_vendor()):
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('orders:my_orders')
    
    # Check if payment exists
    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        payment = None
    
    context = {
        'order': order,
        'payment': payment,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_success(request, order_number):
    """Order success/confirmation page."""
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    
    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        payment = None
    
    context = {
        'order': order,
        'payment': payment,
    }
    return render(request, 'orders/order_success.html', context)


@login_required
def my_orders(request):
    """User's orders."""
    if request.user.is_customer():
        orders = Order.objects.filter(customer=request.user)
    elif request.user.is_vendor():
        # Orders containing vendor's products
        orders = Order.objects.filter(items__product__vendor=request.user).distinct()
    else:
        orders = Order.objects.all()
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'orders/my_orders.html', context)


@login_required
def update_order_status(request, order_number):
    """Update order status (vendor/admin only)."""
    order = get_object_or_404(Order, order_number=order_number)
    
    if not (request.user.is_vendor() or request.user.is_admin()):
        messages.error(request, 'You do not have permission to update order status.')
        return redirect('orders:order_detail', order_number=order_number)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, 'Order status updated successfully!')
        else:
            messages.error(request, 'Invalid status.')
    
    return redirect('orders:order_detail', order_number=order_number)








