package com.ase.angelos_kb_backend.service;

import java.util.HashMap;
import java.util.Map;

import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.stereotype.Service;

import com.ase.angelos_kb_backend.configuration.CustomUserDetails;
import com.ase.angelos_kb_backend.util.JwtUtil;

@Service
public class AuthenticationService {

    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;

    public AuthenticationService(AuthenticationManager authenticationManager, JwtUtil jwtUtil) {
        this.authenticationManager = authenticationManager;
        this.jwtUtil = jwtUtil;
    }

    public Map<String, String> login(String email, String password) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(email, password)
            );

            CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();

            if (!userDetails.isEnabled()) {
                throw new RuntimeException("Login failed: Your account is not yet approved by an administrator.");
            }

            // Retrieve required parameters
            Long orgId = userDetails.getOrgId();
            boolean isSystemAdmin = userDetails.isSystemAdmin();

            // Generate tokens
            String accessToken = jwtUtil.generateToken(email, orgId, isSystemAdmin);
            String refreshToken = jwtUtil.generateRefreshToken(email);

            // Return tokens
            Map<String, String> tokens = new HashMap<>();
            tokens.put("accessToken", accessToken);
            tokens.put("refreshToken", refreshToken);

            return tokens;

        } catch (AuthenticationException ex) {
            throw new RuntimeException("Invalid email or password", ex);
        }
    }
}
