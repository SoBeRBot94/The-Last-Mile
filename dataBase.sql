DROP DATABASE IF EXISTS `LastMile`;

CREATE DATABASE `LastMile`;

use `LastMile`;

DROP TABLE IF EXISTS `employee`;

CREATE TABLE `employee` (
		id INT NOT NULL AUTO_INCREMENT,
		public_id CHAR(50) NOT NULL UNIQUE,
		name CHAR(25) NOT NULL,
		password CHAR(80) NOT NULL,
		admin BOOLEAN NOT NULL,
		PRIMARY KEY(id)
);

DROP TABLE IF EXISTS `vendor`;

CREATE TABLE `vendor` (
		id INT NOT NULL AUTO_INCREMENT,
		public_id CHAR(50) NOT NULL UNIQUE,
		name CHAR(25) NOT NULL,
		password CHAR(80) NOT NULL,
		PRIMARY KEY(id)
);

DROP TABLE IF EXISTS `package`;

CREATE TABLE `package` (
		id INT NOT NULL AUTO_INCREMENT,
		qr_id CHAR(50) NOT NULL UNIQUE,
		name CHAR(25) NOT NULL,
		volume INT NOT NULL,
		vendorName CHAR(25) NOT NULL,
		inception CHAR(25) NOT NULL,
		intraCityDelivery BOOLEAN NOT NULL,
		deliveryLocation CHAR(50) NOT NULL,
		pickupTime TIMESTAMP NOT NULL,
		packageStatus CHAR(10) NOT NULL,
		dropTime TIMESTAMP NOT NULL,
		packageCurrentLocation CHAR(25) NOT NULL,
		PRIMARY KEY(id)
);
