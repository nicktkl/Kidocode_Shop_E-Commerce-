from flask import Blueprint, render_template, request, redirect, url_for
from models import Product, Customer, Order, OrderItem, Payment, Review, db

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/')
def homepage():
    return render_template("/user/homepage.html")

@user_blueprint.route('/productlist')
def productlist():
    products = Product.query.all()
    return render_template("/user/productlist.html", product=products)

@user_blueprint.route('/product', methods=["GET", "POST"])
def product():
    p_ID = request.form.get('p_ID')
    if not p_ID:
        return "Product ID not provided", 400
    product = Product.query.get_or_404(p_ID)
    return render_template("/user/product.html", product=product)
