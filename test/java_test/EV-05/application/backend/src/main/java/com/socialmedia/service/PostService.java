package com.socialmedia.service;

import com.socialmedia.dto.PostRequest;
import com.socialmedia.dto.PostResponse;
import com.socialmedia.model.Post;
import com.socialmedia.model.User;
import com.socialmedia.repository.PostRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PostService {
    private final PostRepository postRepository;
    private final UserService userService;

    public List<PostResponse> getFeed() {
        User currentUser = userService.getCurrentUser();
        
        List<Post> allPosts = postRepository.findAllPosts();
        
        return allPosts.stream()
            .filter(post -> {
                return !post.isPrivate() || // public posts
                       post.getUser().getId().equals(currentUser.getId()) || // own posts
                       (currentUser.getFollowing().contains(post.getUser()) && canViewPost(currentUser, post)); // followed user's posts
            })
            .sorted(Comparator.comparing(Post::getCreatedAt).reversed())
            .map(this::mapToDto)
            .collect(Collectors.toList());
    }

    public List<PostResponse> getPublicPosts() {
        return postRepository.findAllPublicPosts().stream()
            .map(this::mapToDto)
            .collect(Collectors.toList());
    }

    public List<PostResponse> getUserPosts(String username) {
        User currentUser = userService.getCurrentUser();
        User targetUser = userService.getUserByUsername(username);
        
        return postRepository.findByUserOrderByCreatedAtDesc(targetUser).stream()
            .filter(post -> canViewPost(currentUser, post))
            .map(this::mapToDto)
            .collect(Collectors.toList());
    }

    private boolean canViewPost(User viewer, Post post) {
        if (post.getUser().getId().equals(viewer.getId())) {
            return true;
        }

        if (!post.isPrivate()) {
            return true;
        }

        return post.getUser().getFollowers().contains(viewer);
    }

    public PostResponse createPost(PostRequest request) {
        User currentUser = userService.getCurrentUser();
        
        Post post = new Post();
        post.setContent(request.getContent());
        post.setPrivate(request.isPrivate());
        post.setUser(currentUser);
        
        Post savedPost = postRepository.save(post);
        return mapToDto(savedPost);
    }

    public void deletePost(Long postId) {
        Post post = postRepository.findById(postId)
            .orElseThrow(() -> new RuntimeException("Post not found"));
            
        User currentUser = userService.getCurrentUser();
        if (!post.getUser().getId().equals(currentUser.getId())) {
            throw new RuntimeException("Not authorized to delete this post");
        }
        
        postRepository.delete(post);
    }

    public PostResponse getPost(Long id) {
        User currentUser = userService.getCurrentUser();
        Post post = postRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Post not found"));
        
        return mapToDto(post);
    }

    private PostResponse mapToDto(Post post) {
        PostResponse dto = new PostResponse();
        dto.setId(post.getId());
        dto.setContent(post.getContent());
        dto.setCreatedAt(post.getCreatedAt());
        dto.setPrivate(post.isPrivate());
        dto.setUser(userService.mapToDto(post.getUser()));
        return dto;
    }
} 