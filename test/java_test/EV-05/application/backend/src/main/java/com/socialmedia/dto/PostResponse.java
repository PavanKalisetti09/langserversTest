package com.socialmedia.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class PostResponse {
    private Long id;
    private String content;
    private UserDto user;
    private LocalDateTime createdAt;
    private boolean isPrivate;
} 