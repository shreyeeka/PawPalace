// PawPalace - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
                navMenu.classList.remove('active');
            }
        });
    }

    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                event.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // Quantity input validation
    const quantityInputs = document.querySelectorAll('input[type="number"]');
    quantityInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const min = parseInt(this.getAttribute('min')) || 1;
            const max = parseInt(this.getAttribute('max')) || Infinity;
            const value = parseInt(this.value);

            if (value < min) {
                this.value = min;
            } else if (value > max) {
                this.value = max;
            }
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Image lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // Add to cart AJAX (if needed)
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Allow normal form submission for now
            // Can be enhanced with AJAX later
        });
    });

    // Confirm delete actions
    document.querySelectorAll('a[onclick*="confirm"]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            const confirmMessage = this.getAttribute('onclick').match(/'([^']+)'/);
            if (confirmMessage && !confirm(confirmMessage[1])) {
                e.preventDefault();
            }
        });
    });

    // Price range filter
    const priceInputs = document.querySelectorAll('.price-range input');
    priceInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const minPrice = parseFloat(document.querySelector('input[name="min_price"]').value) || 0;
            const maxPrice = parseFloat(document.querySelector('input[name="max_price"]').value) || Infinity;

            if (minPrice > maxPrice && maxPrice !== Infinity) {
                this.setCustomValidity('Minimum price cannot be greater than maximum price');
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // Dropdown menu enhancement
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    dropdowns.forEach(function(dropdown) {
        const link = dropdown.querySelector('.nav-link');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (link && menu) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                // Toggle is handled by CSS :hover
            });
        }
    });

    // Payment method selection
    const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
    if (paymentMethods.length > 0) {
        paymentMethods.forEach(function(method) {
            method.addEventListener('change', function() {
                // This is handled in the template's inline script
                // But we can add additional functionality here if needed
            });
        });
    }

    // Search form enhancement
    const searchForms = document.querySelectorAll('form[method="get"]');
    searchForms.forEach(function(form) {
        const searchInput = form.querySelector('input[name="search"]');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                // Could implement live search here
            });
        }
    });

    // Table row hover effect
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Initialize tooltips (if using a library)
    // Can be enhanced with a tooltip library if needed

    // Buy Now button - update quantity in URL
    const buyNowBtn = document.getElementById('buy-now-btn');
    const quantityInput = document.getElementById('product-quantity');
    if (buyNowBtn && quantityInput) {
        buyNowBtn.addEventListener('click', function(e) {
            const quantity = quantityInput.value || 1;
            this.href = this.href.split('?')[0] + '?quantity=' + quantity;
        });
    }

    console.log('PawPalace - Website initialized');
});

// Utility functions
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = function() {
        notification.remove();
    };
    
    notification.appendChild(closeBtn);
    
    const container = document.querySelector('.messages-container') || document.body;
    container.appendChild(notification);
    
    setTimeout(function() {
        notification.style.opacity = '0';
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 5000);
}








