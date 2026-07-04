from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_POST

import stripe

from orders.models import Order
from .models import Payment
from .forms import PaymentForm


@login_required
def esewa_payment(request, order_number):
    """eSewa payment page (mock)."""
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    
    # Check if payment already exists
    payment, created = Payment.objects.get_or_create(order=order)
    
    if payment.status == 'completed':
        messages.info(request, 'Payment already completed for this order.')
        return redirect('orders:order_success', order_number=order_number)
    
    if request.method == 'POST':
        payment.status = 'completed'
        payment.payment_date = timezone.now()
        payment.payment_method = 'esewa'
        payment.save()
        
        order.status = 'confirmed'
        order.save()
        
        messages.success(request, f'Payment successful! Transaction ID: {payment.transaction_id or "N/A"}')
        return redirect('orders:order_success', order_number=order_number)
    
    context = {
        'order': order,
        'payment': payment,
    }
    return render(request, 'payments/esewa_payment.html', context)


@login_required
def process_payment(request, order_number):
    """Handle COD or eSewa redirect."""
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    
    if hasattr(order, 'payment') and order.payment.status in ['completed', 'pending']:
        messages.info(request, 'Payment already processed for this order.')
        return redirect('orders:order_detail', order_number=order_number)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total,
                status='pending' if payment_method == 'cod' else 'processing'
            )
            
            if payment_method == 'esewa':
                return redirect('payments:esewa_payment', order_number=order_number)
            elif payment_method == 'cod':
                order.status = 'confirmed'
                order.save()
                messages.success(request, 'Order confirmed! Payment will be collected on delivery.')
                return redirect('orders:order_success', order_number=order_number)
    else:
        form = PaymentForm()
    
    context = {'order': order, 'form': form}
    return render(request, 'payments/process_payment.html', context)


@login_required
def payment_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found for this order.')
        return redirect('orders:order_detail', order_number=order_number)
    
    context = {'order': order, 'payment': payment}
    return render(request, 'payments/payment_detail.html', context)


@login_required
def checkout(request):
    """Render Stripe Checkout page."""
    amount = settings.STRIPE_DEFAULT_AMOUNT
    if request.GET.get("amount"):
        try:
            amount = int(request.GET["amount"])
        except (TypeError, ValueError):
            amount = settings.STRIPE_DEFAULT_AMOUNT
    amount = max(50, amount)
    display_amount = f"{amount / 100:.2f}"

    context = {
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "amount": amount,
        "display_amount": display_amount,
        "currency": settings.STRIPE_CURRENCY,
    }
    return render(request, "payments/checkout.html", context)


@require_POST
def create_checkout_session(request):
    """Create a Stripe Checkout session."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    amount = int(request.POST.get("amount", settings.STRIPE_DEFAULT_AMOUNT))
    amount = max(50, amount)

    success_url = request.build_absolute_uri(reverse("payments:payment_success"))
    cancel_url = request.build_absolute_uri(reverse("payments:payment_cancel"))

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "product_data": {"name": "PawPalace Order"},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def payment_success(request):
    return render(request, "payments/success.html")


def payment_cancel(request):
    return render(request, "payments/cancel.html")