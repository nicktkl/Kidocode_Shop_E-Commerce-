from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Branches model
class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    operating_hours = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Branch {self.name}>"

# Category model
class Category(db.Model):
    __tablename__ = 'category'

    categoryID = db.Column(db.String(7), primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    parentID = db.Column(db.String(7), db.ForeignKey('category.categoryID', ondelete='CASCADE'), nullable=True)
    createdAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)
    updatedAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    parent_category = db.relationship('Category', remote_side=[categoryID], backref=db.backref('subcategories', lazy=True))

    def __repr__(self):
        return f"<Category {self.name}>"

# Product model
class Product(db.Model):
    __tablename__ = 'product'

    productID = db.Column(db.String(10), primary_key=True)
    productName = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)
    img = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    categoryID = db.Column(db.String(7), db.ForeignKey('category.categoryID', ondelete='SET NULL'))
    createdAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)
    updatedAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', name='status_enum'), default='active', nullable=False)

    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    order_items = db.relationship('OrderItem', back_populates='product')
    reviews = db.relationship('Review', back_populates='product')

    def __repr__(self):
        return f"<Product {self.productName}, Status: {self.status}>"

# User model
class User(db.Model):
    __tablename__ = 'user'

    userID = db.Column(db.String(4), primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    address = db.Column(db.Text, nullable=True)
    secondaryAddress = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)
    updatedAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    orders = db.relationship('Order', back_populates='user')
    reviews = db.relationship('Review', back_populates='user')
    feedbacks = db.relationship('Feedback', back_populates='user')

    def __repr__(self):
        return f"<User {self.firstName} {self.lastName}>"

# Order model
class Order(db.Model):
    __tablename__ = 'orders'

    orderID = db.Column(db.String(13), primary_key=True)
    userID = db.Column(db.String(4), db.ForeignKey('user.userID', ondelete='CASCADE'), nullable=False)
    totalAmount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(15), nullable=False, default="Processing")
    shippingAddress = db.Column(db.Text, nullable=False)
    shippingMethod = db.Column(db.String(50), nullable=False)
    pickupBranch = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)
    updatedAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    user = db.relationship('User', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order', lazy='dynamic')
    payments = db.relationship('Payment', back_populates='order')

    def __repr__(self):
        return f"<Order {self.orderID} for User {self.userID}>"

# OrderItem model
class OrderItem(db.Model):
    __tablename__ = 'orderitem'

    orderItemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderID = db.Column(db.Integer, db.ForeignKey('orders.orderID', ondelete='CASCADE'), nullable=False)
    productID = db.Column(db.String(5), db.ForeignKey('product.productID', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

    def __repr__(self):
        return f"<OrderItem {self.orderItemID} for Order {self.orderID}>"

# Review model
class Review(db.Model):
    __tablename__ = 'review'

    reviewID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productID = db.Column(db.String(5), db.ForeignKey('product.productID', ondelete='CASCADE'), nullable=False)
    userID = db.Column(db.String(4), db.ForeignKey('user.userID', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    updatedAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    response = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)

    product = db.relationship('Product', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    def __repr__(self):
        return f"<Review {self.reviewID} for Product {self.productID}>"

# Payment model
class Payment(db.Model):
    __tablename__ = 'payment'

    paymentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderID = db.Column(db.String(13), db.ForeignKey('orders.orderID', ondelete='CASCADE'), nullable=False)
    paymentDate = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    deliveryCharge = db.Column(db.Float, nullable=False)  # Added deliveryCharge column
    paymentMethod = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(15), nullable=False)

    order = db.relationship('Order', back_populates='payments')

    def __repr__(self):
        return f"<Payment {self.paymentID} for Order {self.orderID}>"
    
# Feedback model
class Feedback(db.Model):
    __tablename__ = 'feedback'

    feedbackID = db.Column(db.String(4), primary_key=True)
    userID = db.Column(db.String(4), db.ForeignKey('user.userID', ondelete='CASCADE'), nullable=False)
    feedbackType = db.Column(db.Enum('Bug', 'Suggestion', 'Praise', 'Complaint', name='feedback_type'), nullable=False)
    feedbackText = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)
    updatedAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    status = db.Column(db.Enum('Pending', 'Reviewed', 'Resolved', name='feedback_status'), default='Pending', nullable=False)
    response = db.Column(db.Text, nullable=True)
    severity = db.Column(db.Enum('Low', 'Medium', 'High', 'Critical', name='feedback_severity'), nullable=True)

    user = db.relationship('User', back_populates='feedbacks')

    def __repr__(self):
        return f"<Feedback {self.feedbackID}: {self.feedbackType}>"