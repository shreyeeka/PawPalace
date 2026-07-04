from django import forms
from .models import Payment


class PaymentForm(forms.Form):
    """Payment form."""
    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='online'
    )









