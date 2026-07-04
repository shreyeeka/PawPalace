from .models import CartItem


def cart_count(request):
    """Add cart count to context."""
    if request.user.is_authenticated and request.user.is_customer():
        count = CartItem.objects.filter(user=request.user).count()
        return {'cart_count': count}
    return {'cart_count': 0}









