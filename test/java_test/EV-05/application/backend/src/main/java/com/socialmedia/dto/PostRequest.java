package com.socialmedia.dto;

import lombok.Data;

@Data
public class PostRequest {
    private String content;
    private boolean isPrivate;
} 