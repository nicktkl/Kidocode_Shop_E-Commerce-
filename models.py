from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Category model
class Category(db.Model):
    __tablename__ = 'category'
    
    categoryID = db.Column(db.String(7), primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    parentID = db.Column(db.String(7), db.ForeignKey('category.categoryID'), nullable=True)
    createdAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updatedAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Self-referential relationship to handle subcategories
    parent_category = db.relationship('Category', backref=db.backref('subcategories', lazy=True), remote_side=[categoryID])
    
    def __init__(self, categoryID, name, parentID=None):
        self.categoryID = categoryID
        self.name = name
        self.parentID = parentID
    
    def __repr__(self):
        return f"<Category {self.name}>"

# Product model
class Product(db.Model):
    __tablename__ = 'product'

    productID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productName = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)
    img = db.Column(db.String(255), default=None)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    categoryID = db.Column(db.String(7), db.ForeignKey('category.categoryID', ondelete='SET NULL'))
    createdAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)
    updatedAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', name='status_enum'), default='active', nullable=False)

    # Relationship with Category model
    category = db.relationship('Category', backref='products')

    # Relationship with OrderItem (through OrderItem model)
    order_items = db.relationship('OrderItem', back_populates='product')

    # Relationship with Review model
    reviews = db.relationship('Review', back_populates='product')

    def __init__(self, productName, description, price, stock, categoryID, img=None, status='active'):
        self.productName = productName
        self.description = description
        self.price = price
        self.stock = stock
        self.categoryID = categoryID
        self.img = img
        self.status = status

    def __repr__(self):
        return f"<Product {self.productName}, Status: {self.status}>"

# User model
class User(db.Model):
    __tablename__ = 'user'

    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # Store hashed password here
    phone = db.Column(db.String(15), nullable=True)
    address = db.Column(db.Text, nullable=True)
    secondaryAddress = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships with Order and Review
    orders = db.relationship('Order', back_populates='user')
    reviews = db.relationship('Review', back_populates='user')  # Relationship for reviews

    def __repr__(self):
        return f"<User {self.firstName} {self.lastName}>"

# Order model
class Order(db.Model):
    __tablename__ = 'orders'

    orderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID', ondelete='CASCADE'), nullable=False)
    orderDate = db.Column(db.Date, nullable=False)
    totalAmount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(15), nullable=False)
    shippingAddress = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    user = db.relationship('User', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order')
    payments = db.relationship('Payment', back_populates='order')

    def __repr__(self):
        return f"<Order {self.orderID} for User {self.userID}>"

# OrderItem model
class OrderItem(db.Model):
    __tablename__ = 'orderitem'

    orderItemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderID = db.Column(db.Integer, db.ForeignKey('orders.orderID', ondelete='CASCADE'), nullable=False)
    productID = db.Column(db.Integer, db.ForeignKey('product.productID', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

    def __repr__(self):
        return f"<OrderItem {self.orderItemID} for Order {self.orderID}, Product {self.productID}>"

# Review model
class Review(db.Model):
    __tablename__ = 'review'

    reviewID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productID = db.Column(db.Integer, db.ForeignKey('product.productID', ondelete='CASCADE'), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, default=None)
    comment = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

    product = db.relationship('Product', back_populates='reviews') 
    user = db.relationship('User', back_populates='reviews') 

    def __repr__(self):
        return f"<Review {self.reviewID} for Product {self.productID}, User {self.userID}>"

# Payment model
class Payment(db.Model):
    __tablename__ = 'payment'

    paymentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderID = db.Column(db.Integer, db.ForeignKey('orders.orderID', ondelete='CASCADE'), nullable=False)
    paymentDate = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paymentMethod = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(15), nullable=False)

    order = db.relationship('Order', back_populates='payments')

    def __repr__(self):
        return f"<Payment {self.paymentID} for Order {self.orderID}>"
