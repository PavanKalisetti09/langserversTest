package com.socialmedia.controller;

import com.socialmedia.dto.PostResponse;
import com.socialmedia.dto.UserDto;
import com.socialmedia.dto.ErrorResponse;
import com.socialmedia.service.PostService;
import com.socialmedia.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
    private final PostService postService;

    @GetMapping("/me")
    public ResponseEntity<UserDto> getCurrentUser() {
        return ResponseEntity.ok(userService.getCurrentUserDto());
    }

    @GetMapping("/{username}")
    public ResponseEntity<UserDto> getUserProfile(@PathVariable String username) {
        return ResponseEntity.ok(userService.getUserProfile(username));
    }

    @GetMapping("/{username}/posts")
    public ResponseEntity<List<PostResponse>> getUserPosts(@PathVariable String username) {
        return ResponseEntity.ok(postService.getUserPosts(username));
    }

    @GetMapping("/{username}/followers")
    public ResponseEntity<List<UserDto>> getUserFollowers(@PathVariable String username) {
        return ResponseEntity.ok(userService.getFollowers(username));
    }

    @GetMapping("/{username}/following")
    public ResponseEntity<List<UserDto>> getUserFollowing(@PathVariable String username) {
        return ResponseEntity.ok(userService.getFollowing(username));
    }

    @PutMapping("/profile")
    public ResponseEntity<UserDto> updateProfile(@RequestBody UserDto userDto) {
        return ResponseEntity.ok(userService.updateProfile(userDto));
    }

    @GetMapping("/search")
    public ResponseEntity<List<UserDto>> searchUsers(@RequestParam String query) {
        return ResponseEntity.ok(userService.searchUsers(query));
    }

    @PostMapping("/{username}/follow")
    public ResponseEntity<?> followUser(@PathVariable String username) {
        try {
            userService.sendFollowRequest(username);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(new ErrorResponse(e.getMessage()));
        }
    }

    @PostMapping("/{username}/unfollow")
    public ResponseEntity<?> unfollowUser(@PathVariable String username) {
        userService.unfollowUser(username);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/{username}/accept-follow")
    public ResponseEntity<?> acceptFollowRequest(@PathVariable String username) {
        userService.acceptFollowRequest(username);
        return ResponseEntity.ok().build();
    }
} 