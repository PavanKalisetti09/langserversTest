package com.socialmedia.dto;

import lombok.Data;

@Data
public class UserDto {
    private Long id;
    private String username;
    private String email;
    private String bio;
    private boolean isFollowing;
    private boolean followRequestPending;
    private boolean hasRequestedToFollow;
} 