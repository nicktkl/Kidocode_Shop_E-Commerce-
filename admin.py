from flask import Blueprint, render_template, request, redirect, url_for
from models import Category, Product, User, Order, OrderItem, Review, Payment, db
import os
from sqlalchemy.sql import func, desc
from werkzeug.utils import secure_filename

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

#DASHBOARD
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

    product_count = Product.query.count()
    review_count = Review.query.count()
    customer_count = User.query.count()
    payment_count = Payment.query.count()
    total_item_sold = db.session.query(func.sum(OrderItem.quantity)).scalar() or 0
    total_payment_amount = db.session.query(func.sum(Payment.amount)).scalar() or 0

    return render_template(
        "/admin/dashboard.html",
        product_count=product_count,
        review_count=review_count,
        customer_count=customer_count,
        payment_count=payment_count,
        total_payment_amount=total_payment_amount,
        total_item_sold=total_item_sold,
        custlabels=custlabels,
        custdata=custdata,
        salelabels=salelabels,
        saledata=saledata,
        reviewlabels=reviewlabels,
        reviewdata=reviewdata
    )

#CATEGORY
@admin_blueprint.route('/category', methods=["GET","POST"])
def category():
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
                child = Category.query.filter_by(parentID=saveID).all()
                
                try:
                    if category.parentID:  
                        category.name = name
                        category.categoryID = f"{saveID[:6]}{name[0].upper()}"
                    else:
                        category.name = name
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
        
    main_categories = Category.query.filter_by(parentID=None).all()

    return render_template("/admin/category.html", main_categories=main_categories)

#PRODUCT
@admin_blueprint.route('/product', methods=["GET", "POST"])
def product():
    search_query = request.args.get('searchProduct', '')  
    if search_query:
        products = Product.query.filter(
            Product.productName.ilike(f'%{search_query}%') | 
            Product.productID.ilike(f'%{search_query}%')
        ).all()  
    else:
        products = Product.query.all()

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
                    
                new_product = Product(
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
            print(f"Trying to delete product with ID: {deleteID}")
            product = Product.query.get_or_404(deleteID)
            try:
                db.session.delete(product)
                db.session.commit()
                return redirect(url_for('admin.product'))
            except Exception as e:
                db.session.rollback()
                print(f"Error while deleting product: {e}")
                return f"An error occurred while deleting the product: {e}", 500

        if 'btnedit' in request.form:
            productID = request.form.get('btnedit')
            product = Product.query.get_or_404(productID) 
            try:
                product.productName = request.form['p_name']
                product.description = request.form['p_desc']
                product.price = float(request.form['p_price'])
                product.stock = int(request.form['p_stock'])
                db.session.commit()
                return redirect(url_for('admin.product'))
            except Exception as e:
                db.session.rollback()
                return f"An error occurred while updating the product: {e}", 500
    
    category = Category.query.filter_by(parentID=None).all()

    return render_template("/admin/product.html", product=products, category=category)

#CUSTOMER
@admin_blueprint.route('/customer')
def customer():
    search_query = request.args.get('searchCust', '')  
    if search_query:
        user = User.query.filter(
            User.userID.ilike(f'%{search_query}%') |
            User.firstName.ilike(f'%{search_query}%') |
            User.lastName.ilike(f'%{search_query}%')
        ).all()  
    else:
        user = User.query.all()
    return render_template("/admin/customer.html", user=user)

#ORDER
@admin_blueprint.route('/order')
def order():
    search_query = request.args.get('searchOrder', '')  
    if search_query:
        orders = Order.query.filter(
            Order.orderID.ilike(f'%{search_query}%')
        ).all()  
        order_ids = [order.orderID for order in orders]
        orderItems = OrderItem.query.filter(OrderItem.orderID.in_(order_ids)).all()
    else:
        orders = Order.query.all()
        orderItems = OrderItem.query.all()
   
    return render_template("/admin/order.html", order=orders, order_items=orderItems)

#REVIEW
@admin_blueprint.route('/review')
def review():
    search_query = request.args.get('rating', '')  
    if search_query:
        review = Review.query.filter(
            Review.rating.ilike(f'%{search_query}%')
        ).all()  
    else:
        review = Review.query.all()
    return render_template("/admin/review.html", review=review)

#SALE
@admin_blueprint.route('/transaction')
def transaction():
    search_query = request.args.get('searchPayment', '')  
    if search_query:
        payment = Payment.query.filter(
            Payment.paymentID.ilike(f'%{search_query}%')
        ).all()  
    else:
        payment = Payment.query.all()
    return render_template("/admin/transaction.html", payment=payment)
