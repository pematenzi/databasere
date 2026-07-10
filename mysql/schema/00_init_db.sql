
-- Purpose: creating the database and setting up user privileges


DROP DATABASE IF EXISTS university_portal;
CREATE DATABASE university_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE university_portal;

CREATE USER IF NOT EXISTS 'uni_admin'@'localhost' IDENTIFIED BY 'uniadmin';
GRANT ALL PRIVILEGES ON university_portal.* TO 'uni_admin'@'localhost';
FLUSH PRIVILEGES;