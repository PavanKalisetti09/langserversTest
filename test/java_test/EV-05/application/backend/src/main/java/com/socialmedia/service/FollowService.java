package com.socialmedia.service;

import com.socialmedia.dto.UserDto;
import com.socialmedia.model.User;
import com.socialmedia.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class FollowService {
    private final UserRepository userRepository;
    private final UserService userService;

    @Transactional
    public void sendFollowRequest(String username) {
        try {
            User currentUser = userService.getCurrentUser();
            User targetUser = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));
            
            if (currentUser.equals(targetUser)) {
                throw new RuntimeException("Cannot follow yourself");
            }
            
            if (currentUser.getFollowing().contains(targetUser)) {
                throw new RuntimeException("Already following this user");
            }

            if (targetUser.getFollowRequests().contains(currentUser)) {
                throw new RuntimeException("Follow request already sent");
            }
            
            targetUser.getFollowRequests().add(currentUser);
            userRepository.save(targetUser);
        } catch (Exception e) {
            System.err.println("Error in sendFollowRequest: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }

    @Transactional
    public void unfollowUser(String username) {
        try {
            User currentUser = userService.getCurrentUser();
            User targetUser = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));

            if (!targetUser.getFollowers().contains(currentUser)) {
                throw new RuntimeException("Not following this user");
            }

            targetUser.removeFollower(currentUser);
            userRepository.save(targetUser);
        } catch (Exception e) {
            System.err.println("Error in unfollowUser: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }

    public List<UserDto> getFollowRequests() {
        User currentUser = userService.getCurrentUser();
        return currentUser.getFollowRequests().stream()
            .map(userService::mapToDto)
            .collect(Collectors.toList());
    }

    @Transactional
    public void approveFollowRequest(String username) {
        try {
            User currentUser = userService.getCurrentUser();
            User requester = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));

            if (!currentUser.getFollowRequests().contains(requester)) {
                throw new RuntimeException("No follow request from this user");
            }

            currentUser.getFollowRequests().remove(requester);
            currentUser.addFollower(requester);  // requester becomes follower of currentUser
            
            userRepository.save(currentUser);
            userRepository.save(requester);
        } catch (Exception e) {
            System.err.println("Error in approveFollowRequest: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }

    @Transactional
    public void rejectFollowRequest(String username) {
        User currentUser = userService.getCurrentUser();
        User follower = userRepository.findByUsername(username)
            .orElseThrow(() -> new RuntimeException("User not found"));

        if (!currentUser.getFollowRequests().contains(follower)) {
            throw new RuntimeException("No follow request from this user");
        }

        currentUser.getFollowRequests().remove(follower);
        userRepository.save(currentUser);
    }
} 