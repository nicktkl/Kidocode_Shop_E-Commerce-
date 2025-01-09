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
    random_products = random.sample(products, min(len(products), 9))
    reviews = Review.query.filter_by(rating=5).all()

    email = session.get('email', None)
    first_name = session.get('first_name', None)
    if 'cart' not in session:
        session['cart'] = {}
    return render_template('/homepage/HomePage.html', product = random_products, review = reviews, email = email, first_name = first_name)

@user_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    products = Product.query.all()
    random_products = random.sample(products, min(len(products), 9))
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

    return render_template('/user/profile.html', product = random_products, user = user, first_name = first_name)

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
    branch = Branch.query.all()

    cart_items = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())

    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        pickup_location = request.form.get('pickup-location')

        user = User.query.filter_by(email = session['email']).first()
        if not user:
            flash('User not found. Please log in again.', 'danger')
            return redirect(url_for('login'))

        order_id = generateOrderID()

        session['orderID'] = order_id

        order = Order(
            orderID = order_id,  # Assign the generated order ID
            userID = user.userID,
            totalAmount = total_price,
            pickupBranch = "Mont Kiara", #selected_branch['name'] if selected_branch else None,
            shippingAddress = "No address",
            shippingMethod = "Pick up"
        )

        db.session.add(order)
        db.session.commit()

        for name, details in cart_items.items():
            
            product = Product.query.filter_by(productName = name).first()
            
            if not product:
                flash(f"Product '{name}' not found.", 'danger')
                return redirect(url_for('user.checkout'))
            
            order_item = OrderItem(orderID = order.orderID, productID = product.productID, quantity = details['quantity'], price = details['price'])
            db.session.add(order_item)

        db.session.commit()

        # Clear the cart
        session['cart'] = {}
        session.modified = True

        flash(f'Order placed successfully! Your Order ID is {order_id}', 'success')
        return redirect(url_for('user.homepage'))

    return render_template('checkout.html', is_logged_in = True, cart_items = cart_items, total_price = total_price, branch = branch)

#checked
@user_blueprint.route('/payment', methods=['GET', 'POST'])
def payment():
    order = Order.query.filter_by(orderID=session.get('orderID')).first()
    orderItems = OrderItem.query.filter_by(orderID=session.get('orderID')).all()

    if request.method == 'POST':
        if 'btnpay' in request.form:
            method = request.form.get('p_method')
            if method == "Card":
                try:
                    total_amount_in_sen = int(order.totalAmount * 100)
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[
                            {
                                'price_data': {
                                    'currency': 'myr',
                                    'product_data': {
                                        'name': 'Total Order Amount',
                                    },
                                    'unit_amount': total_amount_in_sen,  # Amount in cents ($50.00)
                                },
                                'quantity': 1,
                            },
                        ],
                        mode='payment',
                        success_url=url_for('user.success', _external=True),
                        cancel_url=url_for('user.cancel', _external=True),
                    )

                    return redirect(checkout_session.url, code=303)

                except Exception as e:
                    return str(e)
                
            elif method == "Cash at counter":
                return redirect(url_for('user.success')) 
            
        try:
            payment = Payment(
                orderID = session.get('orderID'),
                amount = order.totalAmount,
                deliveryCharge = 0.00,
                paymentMethod = method,
                status = "Received"
            )

            db.session.add(payment)
            db.session.commit()
            return redirect(url_for('user.home'))
        
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            db.session.rollback()

    return render_template('payment.html', order = order, order_items = orderItems, public_key = Config.STRIPE_PK)

@user_blueprint.route('/success')
def success():
    order = Order.query.filter_by(orderID=session.get('orderID')).first()
    orderItems = OrderItem.query.filter_by(orderID=order.orderID).all()
    payment = Payment.query.filter_by(orderID=order.orderID).first()

    return render_template('thanks.html', order = order, order_items = orderItems, payment = payment)

@user_blueprint.route('/cancel')
def cancel():
    return "Payment canceled. Please try again."

#to generate orderID
def generateOrderID():
    prefix = "KSHOP"
    generate = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return prefix + generate