from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from models import Category, Product, User, Order, OrderItem, Review, Payment, db
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime

import pytz
import random

from user import user_blueprint
from admin import admin_blueprint

bcrypt = Bcrypt()

app = Flask(__name__)

app.secret_key = 'kidocodeverysecretkey'

app.config.update({
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USE_SSL': False,
    'MAIL_USERNAME': 'nurulizzatihayat@gmail.com',
    'MAIL_PASSWORD': 'tmcn fehq fttp smym',
    'MAIL_DEFAULT_SENDER': ('Kidocode', 'nurulizzatihayat@gmail.com')
})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:dlvvkxl@127.0.0.1:3306/ecommerceNEW'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

mail = Mail(app)
db.init_app(app)
bcrypt.init_app(app)
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
    categories = Category.query.all()
    return render_template('/homepage/AllProducts.html', products = products, category = categories)

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
    # Check if the user is logged in
    if session.get('loggedin'):
        return redirect(url_for('user.checkout'))  # Redirect to user.py's checkout

    if request.method == 'POST':
        # Process login form
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # Set user session
            session['loggedin'] = True
            session['email'] = user.email
            session['first_name'] = user.firstName
            flash('Login successful! Redirecting to checkout.', 'success')
            return redirect(url_for('user.checkout'))  # Redirect after login

        flash('Invalid email or password. Please try again.', 'danger')

    # Render login form on checkout.html for guests
    return render_template(
        '/homepage/Checkout.html',
        cart_items=session.get('cart', {}),
        total_price=sum(item['price'] * item['quantity'] for item in session.get('cart', {}).values()),
        is_logged_in=False
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
            return redirect(next_url)
        else:
            flash('Incorrect email or password.', 'danger')
    
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


        userCount = User.query.count()
        newID = f"C{userCount + 1:03d}"
        new_user = User(
            userID = newID,
            email = email, 
            password = hashed_password)

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
    if request.method == 'POST':
        email = request.form['getemail']

        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt='password-reset-salt')

        reset_url = f"http://127.0.0.1:5000/resetpwd/{token}"
        malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
        timestamp = datetime.now(pytz.utc).astimezone(malaysia_tz).strftime('%Y/%m/%d %H:%M GMT')
        try:
            with open("templates/reset-pwd.txt", "r") as file:
                email_body = file.read()
                email_body = email_body.replace("{{ url }}", reset_url)
                email_body = email_body.replace("{{ timestamp }}", timestamp)

            subject = "Password Reset Request"
            msg = Message(subject=subject, recipients=[email], body=email_body)
            mail.send(msg)

            return render_template('/forgot-pass-submitted.html')

        except Exception as e:
            flash(f"An error occurred while sending the email: {e}", 'danger')
            return redirect(url_for('forgotpass'))
        
    return render_template('/forgot-pass.html')

@app.route('/resetpwd/<token>', methods=['GET', 'POST'])
def resetpwd(token):
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)

        if request.method == 'POST':
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if password != confirm_password:
                flash('Passwords do not match, please try again.', 'danger')
                return redirect(url_for('resetpwd', token=token))
            
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = db.session.query(User).filter_by(email=email).first()

            if user:
                user.password = hashed_password
                try:
                    db.session.commit()
                    flash('Your password has been updated successfully!', 'success')
                    return redirect(url_for('login'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'An error occurred: {str(e)}', 'danger')
                    return redirect(url_for('resetpwd', token=token))
            else:
                flash('User not found.', 'danger')
                return redirect(url_for('resetpwd', token=token))

    except Exception as e:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgotpass'))

    return render_template('reset-pass.html', token=token)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    flash('You have been loged out.', 'info')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
