from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
from models import Category, Product, User, Order, OrderItem, Review, Payment, db

import random

from user import user_blueprint
from admin import admin_blueprint

# bcrypt = Bcrypt()

app = Flask(__name__)

app.secret_key = 'kidocodeverysecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@127.0.0.1:3306/ecommerceNEW'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
# bcrypt.init_app(app)
bcrypt = Bcrypt(app)

app.register_blueprint(user_blueprint)
app.register_blueprint(admin_blueprint)

@app.route('/')
def home():
    products = Product.query.all()
    random_products = random.sample(products, min(len(products), 8))
    reviews = Review.query.filter_by(rating=5).all()

    email = session.get('email', None)
    if 'cart' not in session:
        session['cart'] = {}
    return render_template('/homepage/HomePage.html', product = random_products, review = reviews, email = email)

@app.route('/session-check', methods=['GET'])
def session_check():
    return jsonify({'logged_in': session.get('loggedin', False)})

@app.route('/allproducts')
def all_products():
    products = Product.query.all()
    category = Category.query.all()
    return render_template('all_product.html', product = products, category = category)

@app.route('/get-cart', methods = ['GET'])
def get_cart():
    cart = session.get('cart', {})
    return jsonify(session.get('cart', {}))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    total_price = round(total_price, 2)
    cart_list = [
        {'name': name, 'price': details['price'], 'quantity': details['quantity']}
        for name, details in cart_items.items()
    ]
    return render_template('/homepage/Cart.html', cart_items = cart_list, total_price = total_price)

@app.route('/add-to-cart', methods = ['POST'])
def add_to_cart():
    try:
        product_data = request.get_json()
        if not product_data or 'product' not in product_data:
            return jsonify({'success': False, 'message': 'Invalid payload.'}), 400

        product = product_data['product']
        product_name = product.get('name')
        
        if not product_name:
            return jsonify({'success': False, 'message': 'Invalid product name.'}), 400
        
        product_record = Product.query.filter_by(productName=product_name).first()
        if not product_record:
            return jsonify({'success': False, 'message': 'Product not found.'}), 404

        if 'cart' not in session:
            session['cart'] = {}

        if product_name in session['cart']:
            session['cart'][product_name]['quantity'] += 1
        else:
            session['cart'][product_name] = {
                'price': float(product_record.price),
                'image': product_record.img,
                'quantity': 1
            }

        session.modified = True
        return jsonify({'success': True, 'cart': session['cart']})
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error: {str(e)}"}), 500

@app.route('/remove-from-cart', methods = ['POST'])
def remove_from_cart():
    product_name = request.get_json().get('name')
    if 'cart' in session and product_name in session['cart']:
        del session['cart'][product_name]
        session.modified = True
    return jsonify({'success': True, 'cart': session.get('cart', {})})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('loggedin'):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email = email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                session['loggedin'] = True
                session['email'] = user.email
                flash('Login successful! You can now proceed with checkout.', 'success')
                return redirect(url_for('checkout'))
            flash('Invalid email or password. Please try again.', 'danger')

        return render_template(
            '/homepage/Checkout.html',
            cart_items = session.get('cart', {}),
            total_price = sum(item['price'] * item['quantity'] for item in session.get('cart', {}).values()),
            is_logged_in = False
        )
    
    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        city = request.form.get('city')
        state = request.form.get('state')
        postcode = request.form.get('postcode')
        phone = request.form.get('phone')
        cart = session.get('cart', {})
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())

        # Add functions to save order details in the database if needed

        session['cart'] = {}
        session.modified = True

        flash('Order placed successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template(
        '/homepage/Checkout.html',
        cart_items = session.get('cart', {}),
        total_price = sum(item['price'] * item['quantity'] for item in session.get('cart', {}).values()),
        is_logged_in = True
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password_candidate):
            session['loggedin'] = True
            session['email'] = user.email
            session['first_name'] = user.firstName
            next_url = request.args.get('next') or url_for('home')
            flash('Login successful!', 'success')
            return redirect(url_for('user.homepage'))
        else:
            flash('Incorrect e-mail or password.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password does not match, please try again.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(email = email, password = hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Proceed to log in.', 'success')
            print("Login successful, flashing success message")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('register'))

    return render_template('/sign-in.html')

@app.route('/forgotpwd', methods = ['GET', 'POST'])
def forgotpass():
    return render_template('/forgot-pass.html')

if __name__ == "__main__":
    app.run(debug=True)
