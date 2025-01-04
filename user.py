from imports import *
from config import Config

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('loggedin'):
            flash('You need to sign in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@user_blueprint.route('/session-check', methods=['GET'])
def session_check():
    return jsonify({'logged_in': session.get('loggedin', False)})

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

@user_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    email = session.get('email')
    first_name = session.get('first_name')

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
                user.password = Bcrypt.generate_password_hash(password).decode('utf-8')

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.homepage'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')

    return render_template('/user/profile.html', user = user, first_name = first_name)

@user_blueprint.route('/logout')
def logout():
    if session.get('loggedin'):
        session.clear()
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

    branches = [
        {'id': 'MK50480', 'name': 'Solaris Mont Kiara', 'address': 'L-5-1, Solaris Mont Kiara, Jalan Solaris, Off Jalan Duta Kiara, 50480, Kuala Lumpur', 'operating_hours': '10:00 AM - 6:00 PM', 'link': '8qT2dKUGSaUP36hz7'},
        {'id': 'SN47810', 'name': 'Sunway Nexis', 'address': 'A-1-6, Sunway Nexis, Jalan PJU5/1, Kota Damansara, Petaling Jaya 47810, Selangor', 'operating_hours': '10:00 AM - 6:00 PM', 'link': '1dhDr7wAwzcNaWP1A'},
        {'id': 'WF11900', 'name': 'Queens Residences Q2', 'address': '3-1-2, Queens Residences Q2, Jalan Bayan Indah, 11900, Bayan Lepas, Pulau Pinang', 'operating_hours': '10:00 AM - 6:00 PM', 'link': 'qifMavDRWxqAuAit7'},
    ]

    if request.method == 'POST':
        # Process checkout form
        shipping_address = request.form.get('shipping_address')
        pickup_location = request.form.get('pickup-location')
        city = request.form.get('city')
        state = request.form.get('state')
        postcode = request.form.get('postcode')
        phone = request.form.get('phone')

        user = User.query.filter_by(email = session['email']).first()
        if not user:
            flash('User not found. Please log in again.', 'danger')
            return redirect(url_for('login'))
        
        user_id = user.id

        selected_branch = next((branch for branch in branches if branch['id'] == pickup_location), None)

        # Generate a unique order ID
        order_id = generateOrderID()

        # Save order details in the database
        order = Order(
            order_id = order_id,  # Assign the generated order ID
            user_id = user.id,
            user_email = session['email'],
            total_price = total_price,
            pickup_location = selected_branch['name'] if selected_branch else None,
            shipping_address = shipping_address,
            city = city,
            state = state,
            postcode = postcode,
            phone = phone
        )
        db.session.add(order)
        db.session.commit()

        # Save items associated with the order
        for name, details in cart_items.items():
            
            product = Product.query.filter_by(productName = name).first()
            
            if not product:
                flash(f"Product '{name}' not found.", 'danger')
                return redirect(url_for('user.checkout'))
            
            order_item = OrderItem(
                order_id = order.id,
                product_id = product.productID,
                product_name = name,
                quantity = details['quantity'],
                price = details['price']
            )
            db.session.add(order_item)

        db.session.commit()

        # Clear the cart
        session['cart'] = {}
        session.modified = True

        flash(f'Order placed successfully! Your Order ID is {order_id}', 'success')
        return redirect(url_for('user.homepage'))

    return render_template(
        '/homepage/Checkout.html',
        is_logged_in = True,
        cart_items = cart_items,
        total_price = total_price,
        branches = branches
    )

def generateOrderID():
    prefix = "KSHOP"
    generate = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return prefix + generate