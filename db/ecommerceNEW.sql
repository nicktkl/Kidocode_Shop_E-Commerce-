-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: ecommerce
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `categoryID` varchar(7) NOT NULL,
  `name` varchar(50) NOT NULL,
  `parentID` varchar(7) DEFAULT NULL,
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`categoryID`),
  UNIQUE KEY `name` (`name`),
  KEY `parentID` (`parentID`),
  CONSTRAINT `category_ibfk_1` FOREIGN KEY (`parentID`) REFERENCES `category` (`categoryID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES ('3DP001A','Animal','K0013DP','2024-12-21 09:31:30','2024-12-21 09:31:30'),('3DP002V','Vehicle','K0013DP','2024-12-21 09:31:30','2024-12-21 09:31:30'),('3DP003O','Others','K0013DP','2024-12-21 09:31:30','2024-12-21 09:31:30'),('ELE001K','K-Box','K002ELE','2024-12-21 09:31:30','2024-12-21 09:31:30'),('ELE002B','Boards','K002ELE','2024-12-21 09:31:30','2024-12-21 09:31:30'),('ELE003C','Components','K002ELE','2024-12-21 09:31:30','2024-12-21 09:31:30'),('ELE004W','Wires/Cables','K002ELE','2024-12-21 09:31:30','2024-12-21 09:31:30'),('K0013DP','3D Print',NULL,'2024-12-21 09:31:29','2024-12-21 09:31:29'),('K002ELE','Electronics',NULL,'2024-12-21 09:31:29','2024-12-21 09:31:29'),('K003TES','Testing',NULL,'2024-12-21 09:31:55','2024-12-21 09:31:55'),('K004TRI','Trial',NULL,'2024-12-21 09:49:32','2024-12-21 09:49:32'),('TES001E','Elphaba','K003TES','2024-12-21 09:49:48','2024-12-21 09:49:48');
/*!40000 ALTER TABLE `category` ENABLE KEYS */;

--
-- Table structure for table `orderitem`
--

DROP TABLE IF EXISTS `orderitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderitem` (
  `orderItemID` int NOT NULL AUTO_INCREMENT,
  `orderID` int NOT NULL,
  `productID` int NOT NULL,
  `quantity` int NOT NULL,
  `price` double NOT NULL,
  PRIMARY KEY (`orderItemID`),
  KEY `orderID` (`orderID`),
  KEY `productID` (`productID`),
  CONSTRAINT `orderitem_ibfk_1` FOREIGN KEY (`orderID`) REFERENCES `orders` (`orderID`),
  CONSTRAINT `orderitem_ibfk_2` FOREIGN KEY (`productID`) REFERENCES `product` (`productID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderitem`
--

/*!40000 ALTER TABLE `orderitem` DISABLE KEYS */;
INSERT INTO `orderitem` VALUES (1,1,1,1,15.99),(2,1,4,1,25.99),(3,2,6,1,50),(4,3,7,1,28.99),(5,3,9,1,5.99),(6,4,8,1,45.99),(7,5,3,1,12.99),(8,5,5,1,8.99);
/*!40000 ALTER TABLE `orderitem` ENABLE KEYS */;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `orderID` int NOT NULL AUTO_INCREMENT,
  `userID` int NOT NULL,
  `orderDate` date NOT NULL,
  `totalAmount` double NOT NULL,
  `status` varchar(15) NOT NULL,
  `shippingAddress` text NOT NULL,
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`orderID`),
  KEY `fk_customer` (`userID`),
  CONSTRAINT `fk_customer` FOREIGN KEY (`userID`) REFERENCES `user` (`userID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,1,'2024-12-22',41.98,'Completed','123 Main St, City, Country','2024-12-22 10:11:31','2024-12-22 10:11:31'),(2,2,'2024-12-21',50,'Pending','456 Oak Rd, Town, Country','2024-12-22 10:11:31','2024-12-22 10:11:31'),(3,3,'2024-12-20',34.98,'Shipped','789 Pine St, Village, Country','2024-12-22 10:11:31','2024-12-22 10:11:31'),(4,4,'2024-12-19',45.99,'Cancelled','101 Maple Ave, City, Country','2024-12-22 10:11:31','2024-12-22 10:11:31'),(5,5,'2024-12-18',21.98,'Processing','202 Birch Blvd, Town, Country','2024-12-22 10:11:31','2024-12-22 10:11:31');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `paymentID` int NOT NULL AUTO_INCREMENT,
  `orderID` int NOT NULL,
  `paymentDate` date NOT NULL,
  `amount` double NOT NULL,
  `paymentMethod` varchar(30) NOT NULL,
  `status` varchar(15) NOT NULL,
  PRIMARY KEY (`paymentID`),
  KEY `orderID` (`orderID`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`orderID`) REFERENCES `orders` (`orderID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (1,1,'2024-12-22',41.98,'Credit Card','Completed'),(2,2,'2024-12-21',50,'PayPal','Pending'),(3,3,'2024-12-20',34.98,'Debit Card','Shipped'),(4,4,'2024-12-19',45.99,'Credit Card','Cancelled'),(5,5,'2024-12-18',21.98,'Cash on Delivery','Processing');
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `productID` int NOT NULL AUTO_INCREMENT,
  `productName` varchar(30) NOT NULL,
  `description` text,
  `img` varchar(255) DEFAULT NULL,
  `price` double NOT NULL,
  `stock` int NOT NULL,
  `categoryID` varchar(7) DEFAULT NULL,
  `createdAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`productID`),
  KEY `categoryID` (`categoryID`),
  CONSTRAINT `product_ibfk_1` FOREIGN KEY (`categoryID`) REFERENCES `category` (`categoryID`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product`
--

/*!40000 ALTER TABLE `product` DISABLE KEYS */;
INSERT INTO `product` VALUES (1,'3D Printed Cat','A cute 3D printed cat figurine.',NULL,15.99,50,'3DP001A','2024-12-21 09:31:39','2024-12-21 09:31:39'),(2,'3D Printed Dog','A realistic 3D printed dog model.',NULL,20.49,30,'3DP001A','2024-12-21 09:31:39','2024-12-21 09:31:39'),(3,'Mini Race Car','A 3D printed mini race car.',NULL,12.99,40,'3DP002V','2024-12-21 09:31:39','2024-12-21 09:31:39'),(4,'3D Truck Model','A detailed truck model made using 3D printing.',NULL,25.99,25,'3DP002V','2024-12-21 09:31:39','2024-12-21 09:31:39'),(5,'3D Pen Holder','A unique pen holder made using 3D printing.',NULL,8.99,60,'3DP003O','2024-12-21 09:31:39','2024-12-21 09:31:39'),(6,'K-Box Starter Kit','All-in-one K-Box for beginners.',NULL,50,20,'ELE001K','2024-12-21 09:31:39','2024-12-21 09:31:39'),(7,'Arduino Board','Original Arduino Uno R3 development board.',NULL,28.99,15,'ELE002B','2024-12-21 09:31:39','2024-12-21 09:31:39'),(8,'Raspberry Pi 4','A versatile Raspberry Pi 4 board.',NULL,45.99,10,'ELE002B','2024-12-21 09:31:39','2024-12-21 09:31:39'),(9,'LED Lights Pack','A pack of assorted LED lights.',NULL,5.99,100,'ELE003C','2024-12-21 09:31:39','2024-12-21 09:31:39'),(10,'USB Cable','Durable USB-A to USB-C cable.',NULL,3.49,200,'ELE004W','2024-12-21 09:31:39','2024-12-21 09:31:39'),(13,'Testing','12334',NULL,123,123,'K003TES','2024-12-21 09:40:39','2024-12-21 09:40:46');
/*!40000 ALTER TABLE `product` ENABLE KEYS */;

--
-- Table structure for table `review`
--

DROP TABLE IF EXISTS `review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `review` (
  `reviewID` int NOT NULL AUTO_INCREMENT,
  `productID` int NOT NULL,
  `userID` int NOT NULL,
  `rating` int DEFAULT NULL,
  `comment` text,
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`reviewID`),
  KEY `productID` (`productID`),
  KEY `userID` (`userID`),
  CONSTRAINT `review_ibfk_1` FOREIGN KEY (`productID`) REFERENCES `product` (`productID`) ON DELETE CASCADE,
  CONSTRAINT `review_ibfk_2` FOREIGN KEY (`userID`) REFERENCES `user` (`userID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `review`
--

/*!40000 ALTER TABLE `review` DISABLE KEYS */;
INSERT INTO `review` VALUES (1,1,1,5,'Great quality! The 3D printed cat looks amazing.','2024-12-22 11:13:58'),(2,4,1,4,'The 3D truck model is detailed, but could use a little more color.','2024-12-22 11:13:58'),(3,6,2,5,'The K-Box starter kit is perfect for beginners! Easy to use and set up.','2024-12-22 11:13:58'),(4,7,3,4,'Good product, but the Arduino board could have better documentation for beginners.','2024-12-22 11:13:58'),(5,9,3,5,'The LED lights pack was exactly what I needed for my project.','2024-12-22 11:13:58'),(6,8,4,3,'The Raspberry Pi 4 works, but had some issues with connectivity.','2024-12-22 11:13:58'),(7,3,5,5,'The mini race car is a fun model to assemble and works great!','2024-12-22 11:13:58'),(8,5,5,4,'The 3D pen holder is nice, but could have a better design for stability.','2024-12-22 11:13:58');
/*!40000 ALTER TABLE `review` ENABLE KEYS */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `userID` int NOT NULL AUTO_INCREMENT,
  `firstName` varchar(100) NOT NULL,
  `lastName` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `pwd` varchar(255) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `address` text,
  `secondaryAddress` text,
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'John','Doe','john.doe@example.com','password123','1234567890','123 Main St, City, Country',NULL,'2024-12-21 17:43:53','2024-12-21 17:43:53'),(2,'Jane','Smith','jane.smith@example.com','password123','0987654321','456 Oak Rd, Town, Country',NULL,'2024-12-21 17:43:53','2024-12-21 17:43:53'),(3,'Alice','Johnson','alice.johnson@example.com','password123','1122334455','789 Pine St, Village, Country',NULL,'2024-12-21 17:43:53','2024-12-21 17:43:53'),(4,'Bob','Brown','bob.brown@example.com','password123','2233445566','101 Maple Ave, City, Country',NULL,'2024-12-21 17:43:53','2024-12-21 17:43:53'),(5,'Charlie','Davis','charlie.davis@example.com','password123','3344556677','202 Birch Blvd, Town, Country',NULL,'2024-12-21 17:43:53','2024-12-21 17:43:53');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;

--
-- Dumping routines for database 'ecommerce'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-22 11:39:10
