package com.socialmedia.repository;

import com.socialmedia.model.Post;
import com.socialmedia.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface PostRepository extends JpaRepository<Post, Long> {
    List<Post> findByUserOrderByCreatedAtDesc(User user);
    
    @Query("SELECT p FROM Post p WHERE p.isPrivate = false ORDER BY p.createdAt DESC")
    List<Post> findAllPublicPosts();
    
    List<Post> findByUserInOrderByCreatedAtDesc(List<User> users);
    
    @Query("SELECT p FROM Post p WHERE p.user IN :users ORDER BY p.createdAt DESC")
    List<Post> findFeedPosts(List<User> users);
    
    @Query("SELECT p FROM Post p ORDER BY p.createdAt DESC")
    List<Post> findAllPosts();
} 