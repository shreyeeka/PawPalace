from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import Product, Category, Brand
from orders.models import CartItem
from .forms import ProductForm


def home(request):
    """Home page with featured products."""
    featured_products = Product.objects.filter(is_active=True, stock__gt=0)[:8]
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)


def product_list(request):
    """Product listing with search and filters."""
    products = Product.objects.filter(is_active=True)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Brand filter
    brand_slug = request.GET.get('brand', '')
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    
    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sort
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    brands = Brand.objects.filter(products__is_active=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_brand': brand_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """Product detail page."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def category_list(request, slug):
    """Products by category."""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'products/category.html', context)


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.save()
            return redirect('products:vendor_products')   # 🔥 FIXED
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})


@login_required
def edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug, vendor=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products:vendor_products')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'is_edit': True,  # so your template can show "Edit Product"
    }
    return render(request, 'products/add_product.html', context)



@login_required
def delete_product(request, slug):
    """Delete a product."""
    product = get_object_or_404(Product, slug=slug, vendor=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('products:vendor_products')
    return render(request, 'products/delete_product.html', {'product': product})

@login_required
def vendor_products(request):
    products = Product.objects.filter(vendor=request.user)
    return render(request, 'products/vendor_products.html', {'products': products})

