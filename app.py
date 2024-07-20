from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session
import mysql.connector
from decimal import Decimal
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy


import stripe
from dotenv import load_dotenv

# Load environment variables from .env file
# Load environment variables from .env file
dotenv_path = r'C:\Users\bbadh\OneDrive\Desktop\Adharsh_mitraz\Flask\baseenv\E_Commerce_Website_1_original\adharsh1.env'
load_dotenv(dotenv_path=dotenv_path)

# Fetching variables
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
# Configure Stripe
stripe.api_key = STRIPE_SECRET_KEY

print(stripe.api_key)


from flask_mail import Mail, Message


# Print statements for debugging
print(f"STRIPE_PUBLISHABLE_KEY: {STRIPE_PUBLISHABLE_KEY}")
print(f"STRIPE_SECRET_KEY: {STRIPE_SECRET_KEY}")
print(f"SECRET_KEY: {SECRET_KEY}")
print(f"MAIL_SERVER: {MAIL_SERVER}")
print(f"MAIL_PORT: {MAIL_PORT}")
print(f"MAIL_USE_TLS: {MAIL_USE_TLS}")
print(f"MAIL_USERNAME: {MAIL_USERNAME}")
print(f"MAIL_PASSWORD: {MAIL_PASSWORD}")




from flask import Flask
from dotenv import load_dotenv
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)  









# load_dotenv()

app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')



app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable SQLAlchemy modification tracker

# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
api_key = os.getenv('ADHARSH_API_KEY')
  
# db = SQLAlchemy(app)  



# app = Flask(__name__)
app.secret_key = 'sk_test_51PaEMIJ0Ze2hK6ipHsYVI5DrSrokxogo1YJpQLi6oybXu9ZeO3lm5OxgW8E1GgjJeKkr0YUELAvElRBgUDSEWVSN00gHZunZgn'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# MySQL database connection configuration
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Avanthi@8870',
    database='E_commerce1'
)
cursor = db.cursor()
# db = SQLAlchemy(app)  


app.secret_key = SECRET_KEY

app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS.lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

mail = Mail(app)


SQLALCHEMY_DATABASE_URI = 'postgresql://root:Avanthi@8870/E_commerce1'





# @app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        # Insert user into database
        try:
            cursor.execute("INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            db.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_email = request.form['username_email']
        password = request.form['password']
        
        # Check credentials from database
        cursor.execute("SELECT * FROM Users WHERE username = %s OR email = %s", (username_email, username_email))
        user = cursor.fetchone()
        
        if user:
            if password == user[3]:  # Assuming password is stored securely, use hashing in production
                # Successful login
                session['user_id'] = user[0]  # Store user ID in session
                flash('Login successful', 'success')
                return redirect(url_for('products'))
            else:
                flash('Incorrect password', 'error')
                return redirect(url_for('login'))
        else:
            flash('User not found', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/products', methods=['GET'])
def products():
    # Retrieve search query and filter parameters
    search_query = request.args.get('q', '')
    category_filter = request.args.get('category', '')
    brand_filter = request.args.get('brand', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    page = int(request.args.get('page', 1))
    per_page = 6
    offset = (page - 1) * per_page

    # Base query
    query = "SELECT * FROM Products WHERE 1=1"
    filters = []

    # Apply search filter
    if search_query:
        query += " AND (name LIKE %s OR description LIKE %s)"
        filters.extend(['%' + search_query + '%', '%' + search_query + '%'])

    # Apply category filter
    if category_filter:
        query += " AND category = %s"
        filters.append(category_filter)

    # Apply brand filter
    if brand_filter:
        query += " AND brand = %s"
        filters.append(brand_filter)

    # Apply price filter
    if min_price:
        query += " AND price >= %s"
        filters.append(min_price)
    if max_price:
        query += " AND price <= %s"
        filters.append(max_price)

    # Count total products for pagination
    count_query = "SELECT COUNT(*) FROM Products WHERE 1=1"
    count_query_filters = filters[:]

    cursor.execute(count_query + query[len("SELECT * FROM Products WHERE 1=1"):], count_query_filters)
    total_products = cursor.fetchone()[0]

    # Fetch products with filters and pagination
    query += " LIMIT %s OFFSET %s"
    filters.extend([per_page, offset])
    cursor.execute(query, filters)
    products = cursor.fetchall()

    # Fetch distinct categories and brands for filter dropdowns
    cursor.execute("SELECT DISTINCT category FROM Products")
    categories = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT brand FROM Products")
    brands = [row[0] for row in cursor.fetchall()]

    user_id = session.get('user_id')
    # Query to fetch cart items count
    cursor.execute("""
        SELECT COUNT(*) FROM Cart WHERE user_id = %s
    """, (user_id,))
    cart_items_count = cursor.fetchone()[0]    

    return render_template('products.html', products=products, categories=categories, brands=brands,
                           page=page, per_page=per_page, total_products=total_products,cart_items_count=cart_items_count)

# Route for displaying product details
@app.route('/products/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    cursor.execute("SELECT * FROM Products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    user_id = session.get('user_id')
    # Query to fetch cart items count
    cursor.execute("""
        SELECT COUNT(*) FROM Cart WHERE user_id = %s
    """, (user_id,))
    cart_items_count = cursor.fetchone()[0] 

    if product:
        return render_template('product_detail.html', product=product,cart_items_count=cart_items_count)
    else:
        flash('Product not found', 'error')
        return redirect(url_for('products'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Code to send reset password email (not implemented here)
        flash('Password reset email sent', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')





@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('admin_register'))
        
        # Insert admin into database
        try:
            cursor = db.cursor()
            cursor.execute("INSERT INTO Admins (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            db.commit()
            flash('Admin registration successful. Please login.', 'success')
            return redirect(url_for('admin_login'))
        except Exception as e:
            flash(f'Admin registration failed: {str(e)}', 'error')
            return redirect(url_for('admin_register'))
    
    return render_template('admin_register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username_email = request.form['username_email']
        password = request.form['password']
        
        # Check credentials from database
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Admins WHERE username = %s OR email = %s", (username_email, username_email))
        admin = cursor.fetchone()
        
        if admin:
            if password == admin[3]:  # No hashing for simplicity (do not use in production)
                # Successful login
                session['admin_logged_in'] = True
                flash('Admin login successful', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Incorrect password', 'error')
                return redirect(url_for('admin_login'))
        else:
            flash('Admin not found', 'error')
            return redirect(url_for('admin_login'))
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    try:
        # Fetch counts for products, orders, users, and shipping addresses
        cursor.execute("SELECT COUNT(*) AS product_count FROM Products")
        product_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) AS order_count FROM Orders")
        order_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) AS user_count FROM Users")
        user_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) AS address_count FROM ShippingAddresses")
        address_count = cursor.fetchone()[0]

        return render_template('admin_dashboard.html', product_count=product_count, order_count=order_count, user_count=user_count, address_count=address_count)

    except Exception as e:
        error_message = f"Error fetching data: {str(e)}"
        return render_template('error.html', error_message=error_message)
    
            
@app.route('/admin/orders', methods=['GET'])
def admin_orders():
    try:
        page = request.args.get('page', 1, type=int)  # Get page number from query string, default to 1
        per_page = 5  # Number of orders per page

        # Calculate the offset for the SQL query
        offset = (page - 1) * per_page

        # Fetch orders for the current page
        cursor.execute("SELECT * FROM Orders LIMIT %s OFFSET %s", (per_page, offset))
        orders = cursor.fetchall()

        # Example to count total pages
        cursor.execute("SELECT COUNT(*) FROM Orders")
        total_orders = cursor.fetchone()[0]
        total_pages = (total_orders + per_page - 1) // per_page

        return render_template('admin_orders.html', orders=orders, page=page, total_pages=total_pages)
    
    except Exception as e:
        flash(f"Error fetching orders: {str(e)}", 'error')
        return redirect(url_for('admin_orders'))
# Add routes for order details, editing, deleting, etc., as needed
@app.route('/admin/users', methods=['GET'])
def admin_users():
    try:
        page = request.args.get('page', 1, type=int)  # Get page number from query string, default to 1
        per_page = 5  # Number of users per page

        # Calculate the offset for the SQL query
        offset = (page - 1) * per_page

        # Fetch users for the current page
        cursor.execute("SELECT * FROM Users LIMIT %s OFFSET %s", (per_page, offset))
        users = cursor.fetchall()

        # Example to count total pages
        cursor.execute("SELECT COUNT(*) FROM Users")
        total_users = cursor.fetchone()[0]
        total_pages = (total_users + per_page - 1) // per_page

        return render_template('admin_users.html', users=users, page=page, total_pages=total_pages)
    
    except Exception as e:
        flash(f"Error fetching users: {str(e)}", 'error')
        return redirect(url_for('admin_users'))

@app.route('/admin/shippingaddress', methods=['GET'])
def admin_shippingaddress():
    try:
        page = request.args.get('page', 1, type=int)  # Get page number from query string, default to 1
        per_page = 5  # Number of shipping addresses per page

        # Calculate the offset for the SQL query
        offset = (page - 1) * per_page

        # Fetch shipping addresses for the current page
        cursor.execute("SELECT * FROM ShippingAddresses LIMIT %s OFFSET %s", (per_page, offset))
        shipping_addresses = cursor.fetchall()

        # Example to count total pages
        cursor.execute("SELECT COUNT(*) FROM ShippingAddresses")
        total_addresses = cursor.fetchone()[0]
        total_pages = (total_addresses + per_page - 1) // per_page

        return render_template('admin_shippingaddress.html', shipping_addresses=shipping_addresses, page=page, total_pages=total_pages)
    
    except Exception as e:
        flash(f"Error fetching shipping addresses: {str(e)}", 'error')
        return redirect(url_for('admin_shippingaddress'))

# Add routes for user details, editing, deleting, etc., as needed

@app.route('/logout', methods=['GET'])
def logout():
    # Clear session data
    session.pop('user_id', None)  # Example: Clear user_id from session

    # Optional: Perform any other logout tasks, like clearing additional session data

    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

# Route for deleting an order
@app.route('/admin/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    try:
        cursor.execute("DELETE FROM Orders WHERE id = %s", (order_id,))
        db.commit()
        flash('Order deleted successfully', 'success')
    except Exception as e:
        flash(f'Failed to delete order: {str(e)}', 'error')

    return redirect(url_for('admin_orders'))

# Route for deleting a user
@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
        db.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        flash(f'Failed to delete user: {str(e)}', 'error')

    return redirect(url_for('admin_users'))

@app.route('/delete_shipping_address/<int:address_id>', methods=['POST'])
def delete_shipping_address(address_id):
    try:
        cursor.execute("DELETE FROM ShippingAddresses WHERE id = %s", (address_id,))
        db.commit()
        flash('Shipping address deleted successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f"Error deleting shipping address: {str(e)}", 'error')

    # Redirect to the route that lists all shipping addresses
    return redirect(url_for('list_shipping_addresses'))


@app.route('/shipping_addresses', methods=['GET'])
def list_shipping_addresses():
    try:
        cursor.execute("SELECT * FROM ShippingAddresses")
        addresses = cursor.fetchall()
        return render_template('admin_shippingaddress.html', shipping_addresses=addresses)
    except Exception as e:
        error_message = f"Error fetching shipping addresses: {str(e)}"
        return render_template('error.html', error_message=error_message)





























# Route for admin product management panel
@app.route('/admin/products', methods=['GET'])
def admin_products():
    try:
        page = request.args.get('page', 1, type=int)  # Get page number from query string, default to 1
        per_page = 3  # Number of products per page

        # Calculate the offset for the SQL query
        offset = (page - 1) * per_page

        # Fetch products for the current page
        cursor.execute("SELECT * FROM Products LIMIT %s OFFSET %s", (per_page, offset))
        products = cursor.fetchall()

        # Example to count total pages
        cursor.execute("SELECT COUNT(*) FROM Products")
        total_products = cursor.fetchone()[0]
        total_pages = (total_products + per_page - 1) // per_page

        return render_template('admin_products.html', products=products, page=page, total_pages=total_pages)
    
    except Exception as e:
        flash(f"Error fetching products: {str(e)}", 'error')
        return redirect(url_for('admin_products'))
@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        brand = request.form['brand']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uploads_dir = os.path.join(app.root_path, 'static/uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            photo_path = os.path.join(uploads_dir, filename)
            file.save(photo_path)
        
            try:
                cursor.execute("INSERT INTO Products (name, description, price, stock, image_url, category, brand) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                               (name, description, price, stock, filename, category, brand))
                db.commit()
                flash('Product added successfully', 'success')
                return redirect(url_for('admin_products'))
            except Exception as e:
                flash(f"Error adding product: {str(e)}", 'error')
                return redirect(url_for('add_product'))
    
    return render_template('add_product.html')

# Route for editing a product
@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        brand = request.form['brand']
        file = request.files['file']

        try:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                uploads_dir = os.path.join(app.root_path, 'static/uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                photo_path = os.path.join(uploads_dir, filename)
                file.save(photo_path)
                cursor.execute("UPDATE Products SET name=%s, description=%s, price=%s, stock=%s, image_url=%s, category=%s, brand=%s WHERE id=%s",
                               (name, description, price, stock, filename, category, brand, product_id))
            else:
                cursor.execute("UPDATE Products SET name=%s, description=%s, price=%s, stock=%s, category=%s, brand=%s WHERE id=%s",
                               (name, description, price, stock, category, brand, product_id))
            
            db.commit()
            flash('Product updated successfully', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            flash(f'Failed to update product: {str(e)}', 'error')
            return redirect(url_for('edit_product', product_id=product_id))

    cursor.execute("SELECT * FROM Products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    if product:
        return render_template('edit_product.html', product=product)
    else:
        flash('Product not found', 'error')
        return redirect(url_for('admin_products'))
# Route for deleting a product
@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    # Delete product from database
    try:
        cursor.execute("DELETE FROM Products WHERE id = %s", (product_id,))
        db.commit()
        flash('Product deleted successfully', 'success')
    except Exception as e:
        flash(f'Failed to delete product: {str(e)}', 'error')

    return redirect(url_for('admin_products'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        # Initialize cursor
        cursor = db.cursor()

        # Retrieve product_id and quantity from form data
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))
        user_id = session.get('user_id')  # Assuming the user is logged in and their ID is stored in the session

        if not user_id:
            flash('Please log in to add items to your cart.', 'error')
            return redirect(url_for('login'))

        # Check if the product is already in the cart for the user
        cursor.execute("SELECT quantity FROM Cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        result = cursor.fetchone()

        if result:
            # If the product is already in the cart, update the quantity
            new_quantity = result[0] + quantity
            cursor.execute("UPDATE Cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
                           (new_quantity, user_id, product_id))
        else:
            # If the product is not in the cart, insert a new row
            cursor.execute("INSERT INTO Cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                           (user_id, product_id, quantity))

        # Commit changes to the database
        db.commit()

        # Close cursor
        cursor.close()

        flash('Product added to cart!', 'success')
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", 'error')
    except Exception as e:
        flash(f"Error adding product to cart: {str(e)}", 'error')

    return redirect(url_for('products'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id')
    
    try:
        new_quantity = int(float(request.form.get('quantity')))
    except ValueError:
        flash('Invalid quantity value', 'error')
        return redirect(url_for('cart'))

    # Retrieve the user ID from the session
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to update your cart.', 'error')
        return redirect(url_for('login'))

    try:
        # Check if the product is already in the cart for the user
        cursor.execute("SELECT quantity FROM Cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        result = cursor.fetchone()
        
        if result:
            # If the product is in the cart, update the quantity
            cursor.execute("UPDATE Cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
                           (new_quantity, user_id, product_id))
            db.commit()
            flash('Cart updated successfully', 'success')
        else:
            flash('Product not found in cart', 'error')
    except Exception as e:
        flash(f"Error updating cart: {str(e)}", 'error')

    return redirect(url_for('cart'))

# Route for removing from cart
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if request.method == 'POST':
        product_id = request.form['product_id']

        # Remove item from the cart in the database
        try:
            cursor.execute("DELETE FROM Cart WHERE product_id = %s", (product_id,))
            db.commit()
            flash('Item removed from cart successfully', 'success')
        except Exception as e:
            flash(f'Failed to remove item from cart: {str(e)}', 'error')

    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your cart.', 'error')
        return redirect(url_for('login'))
    
     # Query to fetch cart items count
    cursor.execute("""
        SELECT COUNT(*) FROM Cart WHERE user_id = %s
    """, (user_id,))
    cart_items_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT p.id, p.name, p.description, p.price, c.quantity, p.image_url, p.category, p.brand
        FROM Products p
        JOIN Cart c ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()

    total_price = sum(Decimal(item[3]) * item[4] for item in cart_items)
    tax = total_price * Decimal('0.1')  # Assuming 10% tax
    shipping_cost = Decimal('5.0')  # Flat shipping rate

    return render_template('cart.html', cart_items=cart_items, total_price=total_price, tax=tax, shipping_cost=shipping_cost,cart_items_count=cart_items_count)

@app.route('/order_summary', methods=['GET','POST'])
def order_summary():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your order summary.', 'error')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    # Query to fetch cart items count
    cursor.execute("""
        SELECT COUNT(*) FROM Cart WHERE user_id = %s
    """, (user_id,))
    cart_items_count = cursor.fetchone()[0]  

    cursor.execute("""
        SELECT p.id, p.name, p.price, c.quantity, p.image_url
        FROM Products p
        JOIN Cart c ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()

    total_price = sum(Decimal(item[2]) * item[3] for item in cart_items)
    tax = total_price * Decimal('0.1')  # Assuming 10% tax
    shipping_cost = Decimal('5.0')  # Flat shipping rate
    grand_total = total_price + tax + shipping_cost

    return render_template('order_summary.html', cart_items=cart_items, total_price=total_price, tax=tax,
                           shipping_cost=shipping_cost, grand_total=grand_total,cart_items_count=cart_items_count)


@app.route('/ship')
def ship():
    user_id = session.get('user_id')
    user_id = session.get('user_id')



    # Fetch user's previous addresses
    cursor.execute("""
        SELECT * 
        FROM ShippingAddresses 
        WHERE user_id = %s
    """, (user_id,))
    previous_addresses = cursor.fetchall()
    # Query to fetch cart items count
    cursor.execute("""
        SELECT COUNT(*) FROM Cart WHERE user_id = %s
    """, (user_id,))
    cart_items_count = cursor.fetchone()[0] 

    return render_template('shipping_info.html',cart_items_count=cart_items_count,previous_addresses=previous_addresses)


@app.route('/shipping_info', methods=['GET', 'POST'])
def shipping_info():
    if request.method == 'POST':
        # Process shipping info form submission
        fullname = request.form['fullname']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip']

        # Store shipping information in session
        session['shipping_info'] = {
            'fullname': fullname,
            'address': address,
            'city': city,
            'state': state,
            'zip_code': zip_code
        }
        

        try:
            user_id = session.get('user_id')

            # Calculate the grand total
            cursor.execute("""
                SELECT SUM(p.price * c.quantity) as total_price
                FROM Products p
                JOIN Cart c ON c.product_id = p.id
                WHERE c.user_id = %s
            """, (user_id,))
            result = cursor.fetchone()
            total_price = result[0] if result else Decimal('0.00')
            tax = total_price * Decimal('0.1')  # Assuming 10% tax
            shipping_cost = Decimal('5.0')  # Flat shipping rate
            grand_total = total_price + tax + shipping_cost

            # Create an order
            cursor.execute("INSERT INTO Orders (user_id, total_price, status) VALUES (%s, %s, %s)",
                           (user_id, grand_total, 'Pending'))
            db.commit()

            # Retrieve the order_id
            order_id = cursor.lastrowid
            session['order_id'] = order_id
            print(f"Order ID stored in session: {order_id}")  # Debug statement

            # Retrieve cart items
            cursor.execute("""
                SELECT c.product_id, c.quantity, p.price
                FROM Cart c
                JOIN Products p ON c.product_id = p.id
                WHERE c.user_id = %s
            """, (user_id,))
            cart_items = cursor.fetchall()

            if not cart_items:
                print("No items found in the cart for this user.")  # Debug statement
                flash('No items in cart. Please add items to your cart.', 'error')
                return redirect(url_for('checkout'))

            # Insert order items
            for item in cart_items:
                product_id = item[0]
                quantity = item[1]
                price = item[2]

                cursor.execute("""
                    INSERT INTO OrderItems (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, product_id, quantity, price))
                db.commit()
                print(f"Inserted item into OrderItems: Order ID={order_id}, Product ID={product_id}, Quantity={quantity}, Price={price}")  # Debug statement

            # Clear the cart
            cursor.execute("DELETE FROM Cart WHERE user_id = %s", (user_id,))
            db.commit()
            print("Cart cleared for user_id:", user_id)  # Debug statement

            return redirect(url_for('order_confirmation'))

        except Exception as e:
            db.rollback()
            flash(f"Error during order creation: {str(e)}", 'error')
            print(f"Exception during order creation: {str(e)}")  # Debug statement

            return redirect(url_for('order_confirmation'))

    # If it's a GET request or there was an error, render the shipping info form
    return redirect(url_for('order_confirmation'))





@app.route('/select_address', methods=['GET', 'POST'])
def select_address():
    if request.method == 'POST':
        selected_address_id = request.form.get('selected_address')
        if not selected_address_id:
            flash('Please select an address.', 'error')
            return redirect(url_for('select_address'))

        # Fetch selected address details from the database (replace with your actual query)
        cursor.execute("SELECT * FROM ShippingAddresses WHERE user_id = %s", (selected_address_id,))
        address = cursor.fetchone()
        print("address",address)
        if not address:
            flash('Selected address not found.', 'error')
            return redirect(url_for('select_address'))

        # Store selected address in session for checkout
        session['shipping_info'] = {
            'fullname': address['fullname'],
            'address': address['address'],
            'city': address['city'],
            'state': address['state'],
            'zip_code': address['zip_code']
        }


        shipping=session['shipping_info']
        print("shipping info:",shipping)

        # Redirect to checkout page
        return redirect(url_for('checkout'))

    else:
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to select an address.', 'error')
            return redirect(url_for('login'))  # Redirect to login if user not logged in

        # Fetch previous addresses for the user
        cursor.execute("SELECT * FROM ShippingAddresses WHERE user_id = %s", (user_id,))
        previous_addresses = cursor.fetchall()
        return redirect(url_for('order_confirmation'))



@app.route('/checkout_with_address', methods=['GET'])
def checkout_with_address():
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    user_id = session.get('user_id')
    print("user_id:",user_id)

    if not user_id:
        flash('Please log in to checkout.', 'error')
        return redirect(url_for('login'))

    try:
        order_id = session.get('order_id')
        print("order_id",order_id)
        if not order_id:
            flash('Order information missing.', 'error')
            return redirect(url_for('shipping_info'))

        # Fetch selected address details from session
        shipping_info = session.get('shipping_info')
        print("shipping details :",shipping_info)
        if not shipping_info:
            flash('Shipping information is missing.', 'error')
            return redirect(url_for('select_address'))

        # Calculate the grand total
        cursor.execute("SELECT total_price FROM Orders WHERE id = %s", (order_id,))
        result = cursor.fetchone()
        grand_total = result[0] if result else Decimal('0.00')

        print(f"Grand Total: {grand_total}")  # Debug statement
        print("shipping:",shipping_info)

        return render_template('checkout_with_address.html', grand_total=grand_total,
                               STRIPE_PUBLISHABLE_KEY=STRIPE_PUBLISHABLE_KEY, shipping_info=shipping_info)

    except Exception as e:
        flash(f"Error during checkout: {str(e)}", 'error')
        print(f"Exception during checkout: {str(e)}")  # Debug statement
        return redirect(url_for('shipping_info'))














@app.route('/add_address')
def add_address():
    user_id = session.get('user_id')
 
        # Query to fetch cart items count
    cursor.execute("""
        SELECT COUNT(*) FROM Cart WHERE user_id = %s
    """, (user_id,))
    cart_items_count = cursor.fetchone()[0]

    return render_template('add_address.html',cart_items_count=cart_items_count)


@app.route('/order_confirmation', methods=['GET'])
def order_confirmation():
    shipping_info = session.get('shipping_info')
    print("shipping_info",shipping_info)
    if not shipping_info:
        flash('Shipping information is missing.', 'error')
        return redirect(url_for('shipping_info'))

    try:
        order_id = session['order_id']
        user_id = session['user_id']
        print("user_id:",user_id)

        # Insert shipping address into ShippingAddresses table
        cursor.execute("""
            INSERT INTO ShippingAddresses (user_id,order_id, fullname, address, city, state, zip_code)
            VALUES (%s,%s, %s, %s, %s, %s, %s)
        """, (user_id,order_id, shipping_info['fullname'], shipping_info['address'], shipping_info['city'], shipping_info['state'], shipping_info['zip_code']))
        db.commit()
        return redirect(url_for('checkout'))


        return redirect(url_for('checkout'))

    except Exception as e:
        db.rollback()
        flash(f"Error confirming order: {str(e)}", 'error')
        print(f"Error confirming order: {str(e)}")  # Debug statement

        return redirect(url_for('shipping_info')) 

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    user_id = session.get('user_id')

    if not user_id:
        flash('Please log in to checkout.', 'error')
        return redirect(url_for('login'))

    try:
        order_id = session.get('order_id')
        if not order_id:
            flash('Order information missing.', 'error')
            return redirect(url_for('shipping_info'))

        # Calculate the grand total
        cursor.execute("""
            SELECT total_price
            FROM Orders
            WHERE id = %s
        """, (order_id,))
        result = cursor.fetchone()
        grand_total = result[0] if result else Decimal('0.00')

        print(f"Grand Total: {grand_total}")  # Debug statement

        if request.method == 'POST':
            token = request.form.get('stripeToken')
            print(f"Stripe Token: {token}")  # Debug statement

            if not token:
                print("No Stripe token received.")  # Debug statement
                flash('Payment processing error. Please try again.', 'error')
                return redirect(url_for('checkout'))

            try:
                # Process payment with Stripe (example code)
                charge = stripe.Charge.create(
                    amount=int(grand_total * 100),  # Amount in cents
                    currency='usd',
                    source=token,
                    description='Example charge'
                )

                # Handle successful payment
                flash('Payment successful!', 'success')

                # Example: Update order status to 'Paid'
                cursor.execute("""
                    UPDATE Orders
                    SET status = 'Paid'
                    WHERE id = %s
                """, (order_id,))
                db.commit()

                # Redirect to order_success route
                return redirect(url_for('order_success', order_id=order_id))

            except Exception as e:
                flash(f"Error processing payment: {str(e)}", 'error')
                print(f"Error processing payment: {str(e)}")  # Debug statement
                return redirect(url_for('checkout'))

        return render_template('checkout.html', grand_total=grand_total, STRIPE_PUBLISHABLE_KEY=STRIPE_PUBLISHABLE_KEY)

    except Exception as e:
        flash(f"Error during checkout: {str(e)}", 'error')
        print(f"Exception during checkout: {str(e)}")  # Debug statement
        return redirect(url_for('shipping_info'))


@app.route('/order_success/<order_id>', methods=['GET'])
def order_success(order_id):
    try:
        # Fetch order details (assuming you need to display something specific)
        cursor.execute("""
            SELECT fullname, address, city, state, zip_code
            FROM ShippingAddresses
            WHERE order_id = %s
        """, (order_id,))
        result = cursor.fetchone()
        if result:
            fullname, address, city, state, zip_code = result
        else:
            flash('Order details not found.', 'error')
            return redirect(url_for('login'))  # Redirect to home or another page

        # Render order_success.html with necessary data
        return render_template('order_success.html',
                               fullname=fullname,
                               address=address,
                               city=city,
                               state=state,
                               zip_code=zip_code,
                               order_id=order_id)

    except Exception as e:
        flash(f"Error fetching order details: {str(e)}", 'error')
        print(f"Error fetching order details: {str(e)}")  # Debug statement
        return redirect(url_for('login'))  # Redirect to home or another page


@app.route('/process_payment', methods=['POST'])
def process_payment():
    token = request.form['stripeToken']
    grand_total = float(request.form['grand_total'])  # Convert to appropriate type

    try:
        charge = stripe.Charge.create(
            amount=int(grand_total * 100),  # Amount in cents
            currency='usd',
            source=token,
            description='Example charge'
        )
        # Handle successful payment (e.g., update order status, send confirmation email)
        return redirect(url_for('shipping_info'))


    except stripe.error.StripeError as e:
        # Handle Stripe errors (e.g., insufficient funds, card declined)
        return jsonify({'error': str(e)})
    

    




if __name__ == '__main__':
    app.run(debug=True)
