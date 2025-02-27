package com.socialmedia.service;

import com.socialmedia.dto.AuthRequest;
import com.socialmedia.dto.AuthResponse;
import com.socialmedia.dto.RegisterRequest;
import com.socialmedia.dto.UserDto;
import com.socialmedia.model.User;
import com.socialmedia.repository.UserRepository;
import com.socialmedia.security.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    public AuthResponse register(RegisterRequest request) {
        if (userRepository.findByUsername(request.getUsername()).isPresent()) {
            throw new RuntimeException("Username already exists");
        }

        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new RuntimeException("Email already exists");
        }

        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        
        try {
            User savedUser = userRepository.save(user);
            String token = jwtService.generateToken(savedUser);
            
            return AuthResponse.builder()
                .token(token)
                .user(mapToDto(savedUser))
                .build();
        } catch (Exception e) {
            throw new RuntimeException("Failed to register user: " + e.getMessage());
        }
    }

    public AuthResponse login(AuthRequest request) {
        try {
            authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
            );

            User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));
            
            String token = jwtService.generateToken(user);
            
            return AuthResponse.builder()
                .token(token)
                .user(mapToDto(user))
                .build();
        } catch (AuthenticationException e) {
            throw new RuntimeException("Invalid username or password");
        }
    }

    private UserDto mapToDto(User user) {
        UserDto dto = new UserDto();
        dto.setId(user.getId());
        dto.setUsername(user.getUsername());
        dto.setEmail(user.getEmail());
        dto.setBio(user.getBio());
        return dto;
    }
} 