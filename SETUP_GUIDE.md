# PawPalace - Quick Setup Guide

## Step-by-Step Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows users**: If `mysqlclient` fails to install, try:
```bash
pip install mysql-connector-python
```
Then update `core/settings.py` to use `mysql.connector.django` instead of `mysqlclient`.

### 2. Setup MySQL Database

#### Option A: Using MySQL Command Line
```sql
mysql -u root -p
CREATE DATABASE pawpalace_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

#### Option B: Using MySQL Workbench
1. Open MySQL Workbench
2. Create a new database named `pawpalace_db`
3. Set character set to `utf8mb4` and collation to `utf8mb4_unicode_ci`

### 3. Configure Database Settings

Edit `core/settings.py` and update the database configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pawpalace_db',
        'USER': 'root',              # Your MySQL username
        'PASSWORD': 'your_password', # Your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User

```bash
python manage.py createsuperuser
```

Enter username, email, and password when prompted.

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 7. Run the Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Initial Data Setup

### Access Admin Panel
1. Go to http://127.0.0.1:8000/admin/
2. Login with your superuser credentials

### Create Categories
1. Go to Products → Categories
2. Add categories: Food, Toys, Grooming, Accessories, Health, etc.

### Create Service Categories
1. Go to Services → Service Categories
2. Add categories: Grooming, Training, Veterinary, Boarding, etc.

### Create Test Users
1. Register as a Customer at http://127.0.0.1:8000/accounts/register/
2. Register as a Vendor at http://127.0.0.1:8000/accounts/register/ (select Vendor role)
3. Or create users via Admin panel

### Add Products (as Vendor)
1. Login as a vendor
2. Go to Dashboard → Manage Products
3. Click "Add New Product" or use Admin panel
4. Fill in product details and save

### Add Services (as Vendor)
1. Login as a vendor
2. Go to Dashboard → Manage Services
3. Click "Add New Service" or use Admin panel
4. Fill in service details and save

## Testing the Application

### As a Customer:
1. Browse products
2. Add products to cart
3. Checkout and place order
4. Complete payment
5. Book a service
6. View order history

### As a Vendor:
1. Access vendor dashboard
2. Add/edit products
3. Add/edit services
4. View orders
5. Update order status
6. View bookings

### As an Admin:
1. Access admin dashboard
2. Manage all users
3. Manage all products/services
4. View all orders and payments
5. Generate reports

## Common Issues & Solutions

### Issue: MySQL Connection Error
**Solution**: 
- Verify MySQL server is running
- Check database credentials in settings.py
- Ensure database exists

### Issue: Static Files Not Loading
**Solution**:
- Run `python manage.py collectstatic`
- Check DEBUG = True in settings.py
- Clear browser cache

### Issue: Migration Errors
**Solution**:
- Delete all migration files (except __init__.py) in each app
- Run `python manage.py makemigrations` again
- Run `python manage.py migrate`

### Issue: Permission Denied
**Solution**:
- Check user role permissions
- Ensure user is logged in
- Verify URL patterns match user role

## Production Deployment Notes

Before deploying to production:

1. **Update SECRET_KEY**: Generate a new secret key
2. **Set DEBUG = False**: In settings.py
3. **Configure ALLOWED_HOSTS**: Add your domain
4. **Use Environment Variables**: For sensitive data
5. **Setup SSL**: Use HTTPS
6. **Configure Static Files**: Use a proper web server (Nginx/Apache)
7. **Database Backup**: Setup regular backups
8. **Payment Gateway**: Integrate real payment gateway
9. **Email Configuration**: Setup email backend for notifications
10. **Security**: Review Django security checklist

## Support

For issues or questions, refer to:
- Django Documentation: https://docs.djangoproject.com/
- MySQL Documentation: https://dev.mysql.com/doc/

---

Happy Coding! 🐾









