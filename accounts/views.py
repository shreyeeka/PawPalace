from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import User, VendorProfile
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm


def register(request):
    """User registration with role selection."""
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # If vendor, create vendor profile
            if user.role == 'vendor':
                VendorProfile.objects.create(
                    user=user,
                    business_name=form.cleaned_data.get('business_name', ''),
                    business_description=form.cleaned_data.get('business_description', ''),
                )
            
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome to PawPalace, {username}!')
                if user.is_vendor():
                    return redirect('dashboard:vendor_dashboard')
                elif user.is_admin():
                    return redirect('dashboard:admin_dashboard')
                else:
                    return redirect('products:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', None)
                if next_url:
                    return redirect(next_url)
                if user.is_vendor():
                    return redirect('dashboard:vendor_dashboard')
                elif user.is_admin():
                    return redirect('dashboard:admin_dashboard')
                else:
                    return redirect('products:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile(request):
    """User profile view."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'vendor_profile': None,
    }
    
    if request.user.is_vendor() and hasattr(request.user, 'vendor_profile'):
        context['vendor_profile'] = request.user.vendor_profile
    
    return render(request, 'accounts/profile.html', context)









