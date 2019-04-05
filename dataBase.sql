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

DROP TABLE IF EXISTS `inventory`;

CREATE TABLE `inventory` (
		id INT NOT NULL AUTO_INCREMENT,
		qr_id CHAR(50) NOT NULL UNIQUE,
		name CHAR(25) NOT NULL,
		volume INT NOT NULL,
		vendorName CHAR(25) NOT NULL,
		inception CHAR(25) NOT NULL,
		intermediate BOOLEAN NOT NULL,
		interDestWarehouse CHAR(25) NOT NULL,
		pickupTime TIMESTAMP NOT NULL,
		mappedEmployeeID CHAR(25) NOT NULL UNIQUE,
		packageStatus CHAR(10) NOT NULL,
		dropTime TIMESTAMP NOT NULL,
		packageCurrentLocation CHAR(25) NOT NULL,
		PRIMARY KEY(id)
);
