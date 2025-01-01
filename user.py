from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from imports import bcrypt
from models import Category, Product, User, Order, OrderItem, Review, Payment, db
from functools import wraps

import random

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('loggedin'):
            flash('You need to sign in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@user_blueprint.route('/')
@login_required
def homepage():
    products = Product.query.all()
    random_products = random.sample(products, min(len(products), 8))
    reviews = Review.query.filter_by(rating=5).all()

    email = session.get('email', None)
    first_name = session.get('first_name', None)
    if 'cart' not in session:
        session['cart'] = {}
    return render_template('/homepage/HomePage.html', product = random_products, review = reviews, email = email, first_name = first_name)

@user_blueprint.route('/session-check', methods=['GET'])
def session_check():
    return jsonify({'logged_in': session.get('loggedin', False)})

@user_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    email = session.get('email')
    if not email:
        flash('No user logged in.', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')  # Optionally allow password change
        confirm_password = request.form.get('confirm_password')

        if password and password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('profile.html', user=user)
        
        try:
            user.first_name = first_name
            user.last_name = last_name
            if password:  # Update password if provided
                user.password = bcrypt.generate_password_hash(password).decode('utf-8')

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.homepage'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')

    return render_template('/user/profile.html', user=user)

@user_blueprint.route('/logout')
def logout():
    if session.get('loggedin'):
        session.pop('loggedin', None)
        session.pop('email', None)
        session.pop('first_name', None)
        flash('You have been signed out.', 'info')
        return redirect(url_for('home'))

@user_blueprint.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    product_data = request.get_json().get('product')
    product_name = product_data.get('name')

    if not product_name:
        return jsonify({'success': False, 'message': 'Invalid product name.'}), 400

    product = Product.query.filter_by(name=product_name).first()

    if not product:
        return jsonify({'success': False, 'message': 'Product not found.'}), 404

    if 'cart' not in session:
        session['cart'] = {}

    if product_name in session['cart']:
        session['cart'][product_name]['quantity'] += 1
    else:
        session['cart'][product_name] = {
            'price': float(product.price),
            'image': product.img,
            'quantity': 1
        }

    session.modified = True
    return jsonify({'success': True, 'cart': session['cart']})

@user_blueprint.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    total_price = round(total_price, 2)
    cart_list = [
        {'name': name, 'price': details['price'], 'quantity': details['quantity']}
        for name, details in cart_items.items()
    ]
    return render_template('/homepage/Cart.html', cart_items = cart_list, total_price = total_price)

@user_blueprint.route('/get-cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', {})
    return jsonify(cart)

@user_blueprint.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    product_name = request.get_json().get('name')
    if 'cart' in session and product_name in session['cart']:
        del session['cart'][product_name]
        session.modified = True
    return jsonify({'success': True, 'cart': session.get('cart', {})})

@user_blueprint.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())

    if request.method == 'POST':
        # Process checkout form
        shipping_address = request.form.get('shipping_address')
        city = request.form.get('city')
        state = request.form.get('state')
        postcode = request.form.get('postcode')
        phone = request.form.get('phone')

        # Save order details in the database
        # Example: Save order and items
        order = Order(user_email=session['email'], total_price=total_price)
        db.session.add(order)
        db.session.commit()

        for name, details in cart_items.items():
            order_item = OrderItem(order_id=order.id, product_name=name, quantity=details['quantity'], price=details['price'])
            db.session.add(order_item)

        db.session.commit()

        # Clear the cart
        session['cart'] = {}
        session.modified = True

        flash('Order placed successfully!', 'success')
        return redirect(url_for('user.homepage'))

    return render_template(
        '/homepage/Checkout.html',
        is_logged_in=True,
        cart_items=cart_items,
        total_price=total_price
    )