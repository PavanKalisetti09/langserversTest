-- Drop all data but keep tables
DELETE FROM follow_requests;
DELETE FROM user_followers;
DELETE FROM posts;
DELETE FROM users;

-- Reset auto-increment counters
ALTER TABLE users AUTO_INCREMENT = 1;
ALTER TABLE posts AUTO_INCREMENT = 1; 