from flask import Blueprint, render_template, request, redirect, url_for
from models import Category, Product, User, Order, OrderItem, Review, Payment, Feedback, db
import os
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from datetime import datetime
import pytz
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

#DASHBOARD CAN BE BETTER
@admin_blueprint.route('/dashboard')
def dashboard():
    cust_result = db.session.query(
        func.date_format(User.createdAt, '%Y-%u').label('week_date'),
        func.count(User.userID).label('count'),
        func.sum(func.count(User.userID)).over(order_by=func.date_format(User.createdAt, '%Y-%u')).label('cumulative_count')
    ).group_by(func.date_format(User.createdAt, '%Y-%u')).all()

    custlabels = [r.week_date for r in cust_result]
    custdata = [r.cumulative_count for r in cust_result]

    sale_result = db.session.query(
        Product.productName,
        func.sum(OrderItem.quantity).label('total_quantity')
    ).join(OrderItem, Product.productID == OrderItem.productID) \
     .group_by(Product.productID).all()

    salelabels = [r.productName for r in sale_result]
    saledata = [r.total_quantity for r in sale_result]

    review_result = db.session.query(
        Review.rating,
        func.count(Review.rating).label('rating_count')
    ).filter(Review.rating.isnot(None)).group_by(Review.rating).all()

    reviewlabels = [str(r.rating) for r in review_result]
    reviewdata = [r.rating_count for r in review_result]

    product_count = Product.query.count() #total product catalogue
    review_count = Review.query.count() #total review received
    customer_count = User.query.filter(User.userID.ilike('C%')).count() #total customer registered
    total_item_sold = db.session.query(func.sum(OrderItem.quantity)).scalar() or 0
    total_payment_amount = round(db.session.query(func.sum(Payment.amount)).scalar() or 0, 2)


    return render_template(
        "/admin/dashboard.html",
        product_count=product_count,
        review_count=review_count,
        customer_count=customer_count,
        total_payment_amount=total_payment_amount,
        total_item_sold=total_item_sold,
        custlabels=custlabels,
        custdata=custdata,
        salelabels=salelabels,
        saledata=saledata,
        reviewlabels=reviewlabels,
        reviewdata=reviewdata
    )

#CATEGORY DONE
@admin_blueprint.route('/category', methods=["GET","POST"])
def category():
    search_query = request.args.get('searchCategory', '')

    if search_query:
        subquery = Category.query.with_entities(Category.parentID).filter(
            Category.categoryID.ilike(f'%{search_query}%') |
            Category.name.ilike(f'%{search_query}%'),
            Category.parentID.isnot(None)
        ).distinct()

        categories = Category.query.filter(
            (Category.name.ilike(f'%{search_query}%') &
            Category.parentID.is_(None)) | 
            (Category.categoryID.in_(subquery)) 
        ).all()
    else:
        categories = Category.query.filter_by(parentID=None).all()

    if request.method == 'POST':

        if 'btnadd' in request.form:
            name = request.form['c_name']
            parent = request.form.get('c_type', None)

            try:
                if parent:
                    last_3_words = parent.strip()[-3:].upper()
                    category_count = Category.query.filter_by(parentID=parent).count()
                    first_letter = name[0].upper()

                    ID = f"{last_3_words}{category_count + 1:03d}{first_letter}"
                else:
                    total_category_count =  Category.query.filter_by(parentID=None).count()
                    first_three_letters = name.strip()[:3].upper().ljust(3, 'X')
                    ID = f"K{total_category_count + 1:03d}{first_three_letters}"
                    parent = None    

                new_category = Category(
                    name=name,
                    categoryID=ID,
                    parentID=parent
                )

                db.session.add(new_category)
                db.session.commit()
                return redirect(url_for('admin.category'))
            
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                db.session.rollback()
                print(parent)

        elif 'btnsave' in request.form:
            saveID = request.form.get('btnsave')
            name = request.form['sc_name']
            if saveID:
                category = Category.query.get_or_404(saveID)
                
                try:
                    if category.parentID is None:  
                        category.name = name
                        category.categoryID = f"{saveID[:4]}{name.strip()[:3].upper()}"
                    else:
                        category.name = name
                        category.categoryID = f"{saveID[:6]}{name[0].upper()}"
                    db.session.commit()
                    return redirect(url_for('admin.category'))
                except Exception as e:
                    db.session.rollback()
                    return f"An error occurred while saving the category: {e}", 500
            return "Category ID not provided", 400


        elif 'btndelete' in request.form:
            deleteID = request.form.get('btndelete')
            if deleteID:
                category_to_delete = Category.query.filter_by(categoryID=deleteID).first()
                if category_to_delete:
                    try:
                        Category.query.filter_by(parentID=deleteID).delete()
                        db.session.delete(category_to_delete)
                        db.session.commit()
                        return redirect(url_for('admin.category'))
                    except Exception as e:
                        db.session.rollback()
                        return f"An error occurred while deleting the category: {e}", 500
            return "Category ID not provided", 400

    return render_template("/admin/category.html", main_categories=categories)

#PRODUCT DONE
@admin_blueprint.route('/product', methods=["GET", "POST"])
def product():
    search_query = request.args.get('searchProduct', '')  
    filter_status = request.args.get('filter', 'all')
    category_filter = request.args.get('categoryFilter', 'all')

    per_page = 10
    page = request.args.get('page', 1, type=int)

    query = Product.query

    if search_query:
        query = query.filter(
            (Product.productName.ilike(f'%{search_query}%')) | 
            (Product.productID.ilike(f'%{search_query}%'))
        )

    if filter_status == 'active':
        query = query.filter(Product.status == 'active')
    elif filter_status == 'inactive':
        query = query.filter(Product.status == 'inactive')

    if category_filter != 'all':
        query = query.join(Category).filter(Category.parentID == category_filter)

    products = query.paginate(page=page, per_page=per_page, error_out=False)

    if request.method == 'POST':
        if 'btnadd' in request.form:
            try:
                img = request.files['p_img']
                if img:
                    img_filename = secure_filename(img.filename)
                    img_folder = os.path.join('static', 'images')
                    if not os.path.exists(img_folder):
                        os.makedirs(img_folder)
                    img_path = os.path.join('images', img_filename)
                    img.save(os.path.join(img_folder, img_filename))
                else:
                    img_path = None
                
                total_product_count = Product.query.count()
                new_product_id = f"KP{total_product_count + 1:03d}"
                new_product = Product(
                    productID = new_product_id,
                    productName= request.form['p_name'],
                    description= request.form['p_desc'],
                    img = img_path,
                    price= float(request.form['p_price']),
                    stock= int(request.form['p_stock']),
                    categoryID= request.form['p_category']
                )
                db.session.add(new_product)
                db.session.commit()
                return redirect(url_for('admin.product'))
            except Exception as e:
                db.session.rollback()
                return f"An error occurred: {e}"
            
        if 'btndelete' in request.form:
            deleteID = request.form.get('btndelete')
            product = Product.query.get_or_404(deleteID)
            try:
                db.session.delete(product)
                db.session.commit()
                return redirect(url_for('admin.product'))
            except Exception as e:
                db.session.rollback()
                return f"An error occurred while deleting the product: {e}", 500

        if 'btnedit' in request.form:
            productID = request.form.get('btnedit')
            product = Product.query.get_or_404(productID) 
            try:
                product.productName = request.form['p_name']
                product.description = request.form['p_desc']
                product.price = float(request.form['p_price'])
                product.stock = int(request.form['p_stock'])
                product.status = 'active' if request.form.get('p_status') == 'active' else 'inactive'
                db.session.commit()
                return redirect(url_for('admin.product'))
            except Exception as e:
                db.session.rollback()
                return f"An error occurred while updating the product: {e}", 500
    
    category = Category.query.filter_by(parentID=None).all()
    all_categories = Category.query.all()
    category_data = {
        "main_categories": [{"id": cat.categoryID, "name": cat.name} for cat in category],
        "all_categories": [{"id": cat.categoryID, "name": cat.name, "parentID": cat.parentID} for cat in all_categories]
    }

    return render_template("/admin/product.html", product=products, category=category, category_data=category_data)

#CUSTOMER JUSTTHEMAILTHING
@admin_blueprint.route('/customer', methods=["GET", "POST"])
def customer():
    search_query = request.args.get('searchCust', '')  
    if search_query:
        user = User.query.filter(
            (User.userID.ilike(f'%{search_query}%')) |
            (User.firstName.ilike(f'%{search_query}%')) |
            (User.lastName.ilike(f'%{search_query}%'))
        ).all()  
    else:
        user = User.query.all()

    if request.method == 'POST':
        email = request.form['btnmail']
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
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

            return redirect(url_for('admin.customer'))

        except Exception as e:
            print(f"An error occurred while sending the email: {e}", 'danger')
            return redirect(url_for('admin.customer'))
        
    return render_template("/admin/customer.html", user=user)

#ORDER DONE
@admin_blueprint.route('/order')
def order():
    search_query = request.args.get('searchOrder', '')  
    status_filter = request.args.get('statusOrder', '')  
    method_filter = request.args.get('method', '')  

    if search_query:
        orders = Order.query.join(User).filter(
            (Order.orderID == search_query) |
            (Order.userID == search_query) |
            (User.firstName.ilike(f'%{search_query}%')) |
            (User.lastName.ilike(f'%{search_query}%'))
        ).all()
    elif status_filter != "":
        orders = Order.query.filter(
            Order.status.ilike(f'%{status_filter}%')
        ).all()
    elif method_filter != "":
        orders = Order.query.filter(
            Order.shippingMethod.ilike(f'%{method_filter}%')
        ).all()
    else:
        orders = Order.query.all()

    order_ids = [order.orderID for order in orders]
    orderItems = OrderItem.query.filter(OrderItem.orderID.in_(order_ids)).all()

    return render_template("/admin/order.html", order=orders, order_items=orderItems)

#REVIEW DONE
@admin_blueprint.route('/review', methods=["GET", "POST"])
def review():
    search_query = request.args.get('searchReview', '')
    filter_query = request.args.get('ratingSearch', '') 

    if search_query:
        reviews = Review.query.join(Product).join(User).filter(
            (Review.reviewID == search_query) |
            (Review.productID == search_query) |
            (Review.userID == search_query) |
            (Product.productName.ilike(f'%{search_query}%')) |
            (User.firstName.ilike(f'%{search_query}%')) |
            (User.lastName.ilike(f'%{search_query}%'))
        ).all()
    elif filter_query != "":
        reviews = Review.query.filter(
            Review.rating == filter_query
        ).all()
    else:
        reviews = Review.query.all()

    if request.method == 'POST':
        response = request.form['reply']
        id = request.form['btnsend']

        review = Review.query.get_or_404(id)
                
        try:
            review.response = response
            db.session.commit()
            return redirect(url_for('admin.review'))
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {e}", 500

    return render_template("/admin/review.html", review=reviews)

#SALE DONE
@admin_blueprint.route('/transaction', methods=["GET", "POST"])
def transaction():
    search_query = request.args.get('searchPayment', '')
    filter_query = request.args.get('searchStatus', '')  
    if search_query:
        payment = Payment.query.filter(
            (Payment.paymentID == search_query) |
            (Payment.orderID == search_query) |
            (Payment.paymentMethod.ilike(f'%{search_query}%'))
        ).all()
    elif filter_query != "":
        payment = Payment.query.filter(
            Payment.status.ilike(f'%{filter_query}%')
        ).all()
    else:
        payment = Payment.query.all()

    if request.method == 'POST':
        paymentID = request.form.get('btnsave')
        paymentStatus = request.form.get('status')

        try:
            payment = Payment.query.get(paymentID)

            if payment:
                payment.status = paymentStatus
                db.session.commit()
                return redirect(url_for('admin.transaction'))
            else:
                return "Payment not found", 404

        except Exception as e:
            db.session.rollback()
            return f"An error occurred while saving the transaction: {e}", 500
        
    return render_template("/admin/transaction.html", payment=payment)

@admin_blueprint.route('/feedback', methods=["GET", "POST"])
def feedback():
    if request.method == 'POST':
        response = request.form['reply']
        id = request.form['btnsend']

        feedback = Feedback.query.get_or_404(id)
                
        try:
            feedback.response = response
            db.session.commit()
            return redirect(url_for('admin.feedback'))
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {e}", 500

    feedback = Feedback.query.all()

    return render_template("/admin/feedback.html", feedback=feedback)