CREATE DATABASE IF NOT EXISTS job_tracker;
USE job_tracker;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    status ENUM('Applied', 'Shortlisted', 'Interview Scheduled', 'Offer Received', 'Rejected') DEFAULT 'Applied',
    applied_on DATE NOT NULL,
    location VARCHAR(100),
    job_url VARCHAR(255),
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
