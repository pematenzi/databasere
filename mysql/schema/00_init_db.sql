
-- Purpose: creating the database and setting up user privileges


DROP DATABASE IF EXISTS university_portal;
CREATE DATABASE university_portal;

USE university_portal;

CREATE USER IF NOT EXISTS 'uni_admin'@'localhost' IDENTIFIED BY 'uniadmin';
GRANT ALL PRIVILEGES ON university_portal.* TO 'uni_admin'@'localhost';
FLUSH PRIVILEGES;