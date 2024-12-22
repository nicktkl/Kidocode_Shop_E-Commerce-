from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import Category, Product, User, Order, OrderItem, Review, Payment, db
from flask_bcrypt import Bcrypt

import random

from user import user_blueprint
from admin import admin_blueprint

app = Flask(__name__)
app.secret_key = 'kidocodeverysecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:dlvvkxl@127.0.0.1:3306/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
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
    return render_template('/homepage/HomePage.html', product=random_products, review=reviews, email=email)

@app.route('/allproducts')
def all_products():
    products = Product.query.all()
    category = Category.query.all()
    return render_template('all_product.html', product=products, category=category)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    total_price = round(total_price, 2)
    cart_list = [
        {'name': name, 'price': details['price'], 'quantity': details['quantity']}
        for name, details in cart_items.items()
    ]
    return render_template('/homepage/Cart.html', cart_items=cart_list, total_price=total_price)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password_candidate):
            session['loggedin'] = True
            session['email'] = user.email
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
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
        
        new_user = User(email=email, password=hashed_password)

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

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    flash('You have been loged out.', 'info')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
