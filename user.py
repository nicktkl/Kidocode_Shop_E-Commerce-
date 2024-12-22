from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import Product, User, db

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/')
def homepage():
    return render_template("/user/homepage.html")

@user_blueprint.route('/user/add-to-cart', methods=['POST'])
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
            'image_url': product.image_url,
            'quantity': 1
        }

    session.modified = True
    return jsonify({'success': True, 'cart': session['cart']})

@user_blueprint.route('/user/get-cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', {})
    return jsonify(cart)

@user_blueprint.route('/user/remove-from-cart', methods=['POST'])
def remove_from_cart():
    product_name = request.get_json().get('name')
    if 'cart' in session and product_name in session['cart']:
        del session['cart'][product_name]
        session.modified = True
    return jsonify({'success': True, 'cart': session.get('cart', {})})

@user_blueprint.route('/user/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        city = request.form.get('city')
        state = request.form.get('state')
        postcode = request.form.get('postcode')
        phone = request.form.get('phone')
        cart = session.get('cart', {})
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())

        # Save order details in the database if needed

        session['cart'] = {}
        session.modified = True

        flash('Order placed successfully!', 'success')
        return redirect(url_for('home'))
    
    cart_items = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    total_price = round(total_price, 2)
    return render_template('/homepage/Checkout.html', cart_items=cart_items, total_price=total_price)
