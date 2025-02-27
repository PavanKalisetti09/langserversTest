package com.socialmedia.config;

import com.socialmedia.model.Post;
import com.socialmedia.model.User;
import com.socialmedia.repository.PostRepository;
import com.socialmedia.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;

@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {
    private final UserRepository userRepository;
    private final PostRepository postRepository;
    private final PasswordEncoder passwordEncoder;

    @Value("${ADMIN_PASSWORD}")
    private String adminPassword;

    @Value("${FLAG}")
    private String flag;

    @Override
    @Transactional
    public void run(String... args) {
        if (!userRepository.existsByUsername("admin")) {
            User admin = new User();
            admin.setUsername("admin");
            admin.setEmail("admin@example.com");
            admin.setPassword(passwordEncoder.encode(adminPassword));
            admin.setCreatedAt(LocalDateTime.now());
            admin = userRepository.save(admin);

            Post flagPost = new Post();
            flagPost.setContent("Admins's user private posts: " + flag);
            flagPost.setUser(admin);
            flagPost.setCreatedAt(LocalDateTime.now());
            flagPost.setPrivate(true);
            postRepository.save(flagPost);
        }
    }
} 