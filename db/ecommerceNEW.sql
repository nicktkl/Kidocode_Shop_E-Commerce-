-- Active: 1733283387949@@127.0.0.1@3306@ecommerce
CREATE TABLE category (
    categoryID VARCHAR(7) PRIMARY KEY, 
    name VARCHAR(50) NOT NULL UNIQUE,
    parentID VARCHAR(7), 
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    FOREIGN KEY (parentID) REFERENCES category(categoryID) ON DELETE CASCADE
);

INSERT INTO category(categoryID, name)
VALUES
    ('K0013DP', '3D Print'),
    ('K002ELE', 'Electronics');

INSERT INTO category(categoryID, name, parentID)
VALUES
    ('3DP001A', 'Animal', 'K0013DP'),
    ('3DP002V', 'Vehicle', 'K0013DP'),
    ('3DP003O', 'Others', 'K0013DP'),
    ('ELE001K', 'K-Box', 'K002ELE'),
    ('ELE002B', 'Boards', 'K002ELE'),
    ('ELE003C', 'Components', 'K002ELE'),
    ('ELE004W', 'Wires/Cables','K002ELE');

CREATE TABLE product (
  productID int NOT NULL AUTO_INCREMENT,
  productName varchar(30) NOT NULL,
  description text,
  img varchar(255) DEFAULT NULL,
  price double NOT NULL,
  stock int NOT NULL,
  categoryID varchar(7) DEFAULT NULL,
  createdAt timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  status ENUM('active', 'inactive') DEFAULT 'active',  -- Added status column here
  PRIMARY KEY (productID),
  FOREIGN KEY (categoryID) REFERENCES category(categoryID) ON DELETE SET NULL
);

INSERT INTO product (productName, description, price, stock, categoryID)
VALUES 
    ('3D Printed Cat', 'A cute 3D printed cat figurine.', 15.99, 50, '3DP001A'),
    ('3D Printed Dog', 'A realistic 3D printed dog model.', 20.49, 30, '3DP001A'),
    ('Mini Race Car', 'A 3D printed mini race car.', 12.99, 40, '3DP002V'),
    ('3D Truck Model', 'A detailed truck model made using 3D printing.', 25.99, 25, '3DP002V'),
    ('3D Pen Holder', 'A unique pen holder made using 3D printing.', 8.99, 60, '3DP003O'),
    ('K-Box Starter Kit', 'All-in-one K-Box for beginners.', 50.00, 20, 'ELE001K'),
    ('Arduino Board', 'Original Arduino Uno R3 development board.', 28.99, 15, 'ELE002B'),
    ('Raspberry Pi 4', 'A versatile Raspberry Pi 4 board.', 45.99, 10, 'ELE002B'),
    ('LED Lights Pack', 'A pack of assorted LED lights.', 5.99, 100, 'ELE003C'),
    ('USB Cable', 'Durable USB-A to USB-C cable.', 3.49, 200, 'ELE004W');

INSERT INTO product (productName, description, price, stock, categoryID, img, status)
VALUES
    ('Testing 01', 'This product is just a testing due to the current situation is testing.', 9.99, 1, '3DP001A', 'static/images/dummy.png', 'active'),
    ('Testing 02', 'This product is just a testing due to the current situation is testing.', 19.99, 2, '3DP002V', 'static/images/dummy2.png', 'active'),
    ('Testing 03', 'This product is just a testing due to the current situation is testing.', 29.99, 3, '3DP003O', 'static/images/dummy3.png', 'active'),
    ('Testing 04', 'This product is just a testing due to the current situation is testing.', 39.99, 4, 'ELE001K', 'static/images/dummy4.png', 'active'),
    ('Testing 05', 'This product is just a testing due to the current situation is testing.', 49.99, 5, 'ELE002B', 'static/images/dummy5.png', 'active'),
    ('Testing 06', 'This product is just a testing due to the current situation is testing.', 59.99, 6, 'ELE003C', 'static/images/dummy6.png', 'active'),
    ('Testing 07', 'This product is just a testing due to the current situation is testing.', 69.99, 7, 'ELE004W', 'static/images/dummy7.png', 'active'),
    ('Testing 08', 'This product is just a testing due to the current situation is testing.', 79.99, 8, 'ELE004W', 'static/images/dummy8.png', 'active'),
    ('Testing 09', 'This product is just a testing due to the current situation is testing.', 89.99, 9, 'ELE003C', 'static/images/dummy9.png', 'active'),
    ('Testing 10', 'This product is just a testing due to the current situation is testing.', 99.99, 10, 'ELE002B', 'static/images/dummy10.png', 'active'),
    ('Testing 11', 'This product is just a testing due to the current situation is testing.', 109.99, 11, 'ELE001K', 'static/images/dummy11.png', 'active'),
    ('Testing 12', 'This product is just a testing due to the current situation is testing.', 119.99, 12, '3DP003O', 'static/images/dummy12.png', 'active'),
    ('Testing 13', 'This product is just a testing due to the current situation is testing.', 129.99, 13, '3DP002V', 'static/images/dummy13.png', 'active'),
    ('Testing 14', 'This product is just a testing due to the current situation is testing.', 139.99, 14, '3DP001A', 'static/images/dummy14.png', 'active');


CREATE TABLE user (
  userID int NOT NULL AUTO_INCREMENT,
  firstName varchar(100) DEFAULT NULL,
  lastName varchar(100) DEFAULT NULL,
  email varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  phone varchar(15) DEFAULT NULL,
  address text,
  secondaryAddress text,
  createdAt datetime DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (userID),
  UNIQUE KEY email (email)
);

INSERT INTO user (firstName, lastName, email, pwd, phone, address)
VALUES
('John', 'Doe', 'john.doe@example.com', 'password123', '1234567890', '123 Main St, City, Country'),
('Jane', 'Smith', 'jane.smith@example.com', 'password123', '0987654321', '456 Oak Rd, Town, Country'),
('Alice', 'Johnson', 'alice.johnson@example.com', 'password123', '1122334455', '789 Pine St, Village, Country'),
('Bob', 'Brown', 'bob.brown@example.com', 'password123', '2233445566', '101 Maple Ave, City, Country'),
('Charlie', 'Davis', 'charlie.davis@example.com', 'password123', '3344556677', '202 Birch Blvd, Town, Country');

CREATE TABLE orders (
  orderID INT NOT NULL AUTO_INCREMENT,
  userID INT NOT NULL,
  orderDate DATE NOT NULL,
  totalAmount DOUBLE NOT NULL,
  status VARCHAR(15) NOT NULL,
  shippingAddress TEXT NOT NULL,
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
  updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (orderID),
  CONSTRAINT fk_customer FOREIGN KEY (userID) REFERENCES user(userID) ON DELETE CASCADE
);

INSERT INTO orders (userID, orderDate, totalAmount, status, shippingAddress)
VALUES
(1, '2024-12-22', 41.98, 'Completed', '123 Main St, City, Country'),
(2, '2024-12-21', 50.00, 'Pending', '456 Oak Rd, Town, Country'),
(3, '2024-12-20', 34.98, 'Shipped', '789 Pine St, Village, Country'),
(4, '2024-12-19', 45.99, 'Cancelled', '101 Maple Ave, City, Country'),
(5, '2024-12-18', 21.98, 'Processing', '202 Birch Blvd, Town, Country');

CREATE TABLE orderitem (
  orderItemID INT NOT NULL AUTO_INCREMENT,
  orderID INT NOT NULL,
  productID INT NOT NULL,
  quantity INT NOT NULL,
  price DOUBLE NOT NULL,
  PRIMARY KEY (orderItemID),
  FOREIGN KEY (orderID) REFERENCES orders (orderID),
  FOREIGN KEY (productID) REFERENCES product (productID)
);

INSERT INTO orderitem (orderID, productID, quantity, price)
VALUES
(1, 1, 1, 15.99),
(1, 4, 1, 25.99),
(2, 6, 1, 50.00),
(3, 7, 1, 28.99),
(3, 9, 1, 5.99),
(4, 8, 1, 45.99),
(5, 3, 1, 12.99),
(5, 5, 1, 8.99);

CREATE TABLE review (
  reviewID INT NOT NULL AUTO_INCREMENT,
  productID INT NOT NULL,
  userID INT NOT NULL,
  rating INT DEFAULT NULL,
  comment TEXT,
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (reviewID),
  FOREIGN KEY (productID) REFERENCES product(productID) ON DELETE CASCADE,
  FOREIGN KEY (userID) REFERENCES user(userID) ON DELETE CASCADE
);

INSERT INTO review (productID, userID, rating, comment)
VALUES
(1, 1, 5, 'Great quality! The 3D printed cat looks amazing.'),
(4, 1, 4, 'The 3D truck model is detailed, but could use a little more color.'),
(6, 2, 5, 'The K-Box starter kit is perfect for beginners! Easy to use and set up.'),
(7, 3, 4, 'Good product, but the Arduino board could have better documentation for beginners.'),
(9, 3, 5, 'The LED lights pack was exactly what I needed for my project.'),
(8, 4, 3, 'The Raspberry Pi 4 works, but had some issues with connectivity.'),
(3, 5, 5, 'The mini race car is a fun model to assemble and works great!'),
(5, 5, 4, 'The 3D pen holder is nice, but could have a better design for stability.');

CREATE TABLE payment (
  paymentID int NOT NULL AUTO_INCREMENT,
  orderID int NOT NULL,
  paymentDate date NOT NULL,
  amount double NOT NULL,
  paymentMethod varchar(30) NOT NULL,
  status varchar(15) NOT NULL,
  PRIMARY KEY (paymentID),
  FOREIGN KEY (orderID) REFERENCES orders(orderID) ON DELETE CASCADE
);

INSERT INTO payment (orderID, paymentDate, amount, paymentMethod, status)
VALUES
(1, '2024-12-22', 41.98, 'Credit Card', 'Completed'),
(2, '2024-12-21', 50.00, 'PayPal', 'Pending'),
(3, '2024-12-20', 34.98, 'Debit Card', 'Shipped'),
(4, '2024-12-19', 45.99, 'Credit Card', 'Cancelled'),
(5, '2024-12-18', 21.98, 'Cash on Delivery', 'Processing');