package com.socialmedia.service;

import com.socialmedia.dto.UserDto;
import com.socialmedia.model.User;
import com.socialmedia.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;

    public User getCurrentUser() {
        String username = SecurityContextHolder.getContext().getAuthentication().getName();
        return userRepository.findByUsername(username)
            .orElseThrow(() -> new RuntimeException("User not found"));
    }

    public UserDto getUserProfile(String username) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new RuntimeException("User not found"));
        return mapToDto(user);
    }

    public List<UserDto> getFollowers(String username) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new RuntimeException("User not found"));
        return user.getFollowers().stream()
            .map(this::mapToDto)
            .collect(Collectors.toList());
    }

    public List<UserDto> getFollowing(String username) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new RuntimeException("User not found"));
        return user.getFollowing().stream()
            .map(this::mapToDto)
            .collect(Collectors.toList());
    }

    public UserDto mapToDto(User user) {
        User currentUser = getCurrentUser();
        UserDto dto = new UserDto();
        dto.setId(user.getId());
        dto.setUsername(user.getUsername());
        dto.setEmail(user.getEmail());
        dto.setBio(user.getBio());
        dto.setFollowing(user.getFollowers().contains(currentUser));
        dto.setFollowRequestPending(user.getFollowRequests().contains(currentUser));
        dto.setHasRequestedToFollow(currentUser.getFollowRequests().contains(user));
        return dto;
    }

    public UserDto getCurrentUserDto() {
        return mapToDto(getCurrentUser());
    }

    public UserDto updateProfile(UserDto userDto) {
        User currentUser = getCurrentUser();
        currentUser.setBio(userDto.getBio());
        return mapToDto(userRepository.save(currentUser));
    }

    public List<UserDto> searchUsers(String query) {
        return userRepository.findByUsernameContainingIgnoreCase(query).stream()
            .map(this::mapToDto)
            .collect(Collectors.toList());
    }

    public void sendFollowRequest(String username) {
        User currentUser = getCurrentUser();
        User targetUser = getUserByUsername(username);
        
        if (currentUser.equals(targetUser)) {
            throw new RuntimeException("Cannot follow yourself");
        }
        
        targetUser.getFollowRequests().add(currentUser);
        userRepository.save(targetUser);
    }

    public void unfollowUser(String username) {
        User currentUser = getCurrentUser();
        User targetUser = getUserByUsername(username);
        
        targetUser.getFollowers().remove(currentUser);
        userRepository.save(targetUser);
    }

    public void acceptFollowRequest(String username) {
        User currentUser = getCurrentUser();
        User follower = getUserByUsername(username);
        
        if (!currentUser.getFollowRequests().contains(follower)) {
            throw new RuntimeException("No follow request from this user");
        }
        
        currentUser.getFollowRequests().remove(follower);
        currentUser.getFollowers().add(follower);
        userRepository.save(currentUser);
    }

    public User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
            .orElseThrow(() -> new RuntimeException("User not found: " + username));
    }
} 