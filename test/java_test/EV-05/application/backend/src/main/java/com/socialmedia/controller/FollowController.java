package com.socialmedia.controller;

import com.socialmedia.dto.ErrorResponse;
import com.socialmedia.dto.UserDto;
import com.socialmedia.service.FollowService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/follow")
@RequiredArgsConstructor
public class FollowController {

    private final FollowService followService;

    @PostMapping("/{username}")
    public ResponseEntity<?> sendFollowRequest(@PathVariable String username) {
        try {
            followService.sendFollowRequest(username);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(new ErrorResponse(e.getMessage()));
        }
    }

    @DeleteMapping("/{username}")
    public ResponseEntity<?> unfollowUser(@PathVariable String username) {
        try {
            followService.unfollowUser(username);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(new ErrorResponse(e.getMessage()));
        }
    }

    @GetMapping("/requests")
    public ResponseEntity<List<UserDto>> getFollowRequests() {
        return ResponseEntity.ok(followService.getFollowRequests());
    }

    @PostMapping("/{username}/approve")
    public ResponseEntity<?> approveFollowRequest(@PathVariable String username) {
        try {
            followService.approveFollowRequest(username);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(new ErrorResponse(e.getMessage()));
        }
    }

    @PostMapping("/{username}/reject")
    public ResponseEntity<?> rejectFollowRequest(@PathVariable String username) {
        try {
            followService.rejectFollowRequest(username);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(new ErrorResponse(e.getMessage()));
        }
    }
} 