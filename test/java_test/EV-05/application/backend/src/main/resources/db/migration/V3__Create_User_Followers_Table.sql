CREATE TABLE user_followers (
    following_id BIGINT NOT NULL,
    follower_id BIGINT NOT NULL,
    PRIMARY KEY (following_id, follower_id),
    FOREIGN KEY (following_id) REFERENCES users(id),
    FOREIGN KEY (follower_id) REFERENCES users(id)
); 