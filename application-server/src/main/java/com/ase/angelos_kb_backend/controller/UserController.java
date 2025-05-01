package com.ase.angelos_kb_backend.controller;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpCookie;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.web.bind.annotation.CookieValue;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.ase.angelos_kb_backend.configuration.CustomUserDetails;
import com.ase.angelos_kb_backend.dto.LoginRequestDTO;
import com.ase.angelos_kb_backend.dto.RegisterRequestDTO;
import com.ase.angelos_kb_backend.dto.UserDTO;
import com.ase.angelos_kb_backend.dto.UserDetailsDTO;
import com.ase.angelos_kb_backend.exception.UnauthorizedException;
import com.ase.angelos_kb_backend.service.AuthenticationService;
import com.ase.angelos_kb_backend.service.UserService;
import com.ase.angelos_kb_backend.util.JwtUtil;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;
    private final UserDetailsService userDetailsService;
    private final AuthenticationService authenticationService;
    private final JwtUtil jwtUtil;
    @Value("${app.cookie.secure}")
    private boolean secureCookie;



    public UserController(UserService userService, UserDetailsService userDetailsService, AuthenticationService authenticationService, JwtUtil jwtUtil) {
        this.userService = userService;
        this.userDetailsService = userDetailsService;
        this.authenticationService = authenticationService;
        this.jwtUtil = jwtUtil;
    }
    
    @GetMapping
    public ResponseEntity<List<UserDTO>> getAllUsers(@RequestHeader("Authorization") String token) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        List<UserDTO> users = userService.getAllUsersByOrgId(orgId);
        return ResponseEntity.ok(users);
    }

    @GetMapping("/me")
    public ResponseEntity<UserDetailsDTO> getCurrentUser(@RequestHeader("Authorization") String token) {
        String email = jwtUtil.extractEmail(token.replace("Bearer ", ""));
        UserDetailsDTO user = userService.findMe(email);
        return ResponseEntity.ok(user);
    }

    /**
     * Approve a user by ID.
     */
    @PatchMapping("/{userId}/approve")
    public ResponseEntity<UserDTO> approveUser(
            @RequestHeader("Authorization") String token,
            @PathVariable Long userId) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        UserDTO updatedUser = userService.approveUser(userId, orgId);
        return ResponseEntity.ok(updatedUser);
    }

    /**
     * Set a user to admin by ID.
     */
    @PatchMapping("/{userId}/set-admin")
    public ResponseEntity<UserDTO> setUserToAdmin(
            @RequestHeader("Authorization") String token,
            @PathVariable Long userId) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        UserDTO updatedUser = userService.setUserToAdmin(userId, orgId);
        return ResponseEntity.ok(updatedUser);
    }

    /**
     * Remove a user from the organisation by making the user unconfirmed again.
     */
    @PatchMapping("/{userId}/remove")
    public ResponseEntity<UserDTO> removeUserFromOrg(
            @RequestHeader("Authorization") String token,
            @PathVariable Long userId) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        UserDTO updatedUser = userService.removeUser(userId, orgId);
        return ResponseEntity.ok(updatedUser);
    }

    /**
     * Register a new user.
     */
    @PostMapping("/register")
    public ResponseEntity<UserDTO> registerUser(@RequestBody RegisterRequestDTO registerRequest) {
        UserDTO newUser = userService.registerUser(registerRequest.getEmail(), registerRequest.getPassword(), registerRequest.getOrgId());
        return ResponseEntity.ok(newUser);
    }

    /**
     * Confirm user email using the confirmation token.
     */
    @GetMapping("/confirm")
    public ResponseEntity<String> confirmEmail(@RequestParam("token") String token) {
        boolean isConfirmed = userService.confirmUserEmail(token);
        if (isConfirmed) {
            return ResponseEntity.ok("Email confirmed successfully.");
        } else {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Invalid or expired confirmation token.");
        }
    }

    /**
     * Login endpoint.
     */
    @PostMapping("/login")
    public ResponseEntity<Map<String, String>> login(@RequestBody LoginRequestDTO loginRequest) {
        Map<String, String> tokens = authenticationService.login(loginRequest.getEmail(), loginRequest.getPassword());
        
        // The response may contain the access token in the body and the refresh token as a cookie
        HttpCookie refreshCookie = ResponseCookie.from("refreshToken", tokens.get("refreshToken"))
            .httpOnly(true)
            .secure(secureCookie)
            .sameSite("Lax") // For cross-site requests, None is required when sending cookies
            .path("/")
            .maxAge(7 * 24 * 60 * 60) // Refresh token expiry, say one week
            .build();

        return ResponseEntity.ok()
            .header(HttpHeaders.SET_COOKIE, refreshCookie.toString())
            .body(Map.of("accessToken", tokens.get("accessToken")));
    }

    @PostMapping("/refresh")
    public ResponseEntity<Map<String, String>> refreshAccessToken(
            @CookieValue(value = "refreshToken", required = false) String refreshToken) {
        if (refreshToken == null || refreshToken.isEmpty()) {
            System.out.println("Refreshing token failed...");
            return ResponseEntity.badRequest().body(Map.of("error", "Refresh token is required"));
        }
        try {
            String email = jwtUtil.extractEmail(refreshToken);
            UserDetails userDetails = userDetailsService.loadUserByUsername(email);

            if (!jwtUtil.validateToken(refreshToken, userDetails)) {
                throw new UnauthorizedException("Invalid refresh token");
            }

            Long orgId = ((CustomUserDetails) userDetails).getOrgId();
            boolean isSystemAdmin = ((CustomUserDetails) userDetails).isSystemAdmin();
            String newAccessToken = jwtUtil.generateToken(email, orgId, isSystemAdmin);

            System.out.println("Refreshing token success..");
            return ResponseEntity.ok(Map.of("accessToken", newAccessToken));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Invalid or expired refresh token"));
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout() {
        // Create a cookie with the same name and attributes but zero max-age to remove it
        HttpCookie invalidCookie = ResponseCookie.from("refreshToken", "")
            .httpOnly(true)
            .secure(secureCookie)
            .sameSite("Strict")
            .path("/")
            .maxAge(0) // Invalidate the cookie immediately
            .build();

        return ResponseEntity.ok()
            .header(HttpHeaders.SET_COOKIE, invalidCookie.toString())
            .build();
    }
}
