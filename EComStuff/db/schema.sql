CREATE DATABASE kidocodeshop_users;
USE kidocodeshop_users;

CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NOT NULL,
    contactNumber INT NOT NULL,
    userAddress VARCHAR(100) NOT NULL,
    cityAddress VARCHAR(50) NOT NULL,
    stateAddress VARCHAR(50) NOT NULL,
    postcodeAddress INT(5) NOT NULL
);

CREATE TABLE products(
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    category_id INT,
    image_url VARCHAR(255), -- To store URL or file path of product's image.
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);