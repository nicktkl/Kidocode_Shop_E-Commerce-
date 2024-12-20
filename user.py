from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import Product, User, Order, OrderItem, Payment, Review, db

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/')
def homepage():
    return render_template("/user/homepage.html")

@user_blueprint.route('/user/add-to-cart', methds=['POST'])
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
#routes here
