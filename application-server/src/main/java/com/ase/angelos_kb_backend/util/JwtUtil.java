package com.ase.angelos_kb_backend.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import java.util.Date;

import javax.crypto.SecretKey;

@Component
public class JwtUtil {

    private final SecretKey signingKey;

    public JwtUtil(@Value("${jwt.secret.key}") String secretKey) {
        this.signingKey = Keys.hmacShaKeyFor(secretKey.getBytes());
    }

    // Generate JWT Token
    public String generateToken(String email, Long orgId, boolean isSystemAdmin) {
        // 15 minutes
        long ACCESS_TOKEN_EXPIRATION = 15 * 60 * 1000;
        return Jwts.builder()
                .setSubject(email)
                .claim("orgId", orgId) // Include organisation ID in the token
                .claim("isSystemAdmin", isSystemAdmin)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + ACCESS_TOKEN_EXPIRATION))
                .signWith(signingKey, SignatureAlgorithm.HS256)
                .compact();
    }

    // Generate JWT Token
    public String generateChatToken(String email, String password) {
        return Jwts.builder()
                .setSubject(email)
                .claim("password", password)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 1000 * 60 * 60 * 10)) // 10 hours
                .signWith(signingKey, SignatureAlgorithm.HS256)
                .compact();
    }

    // Generate Refresh Token
    public String generateRefreshToken(String email) {
        return Jwts.builder()
                .setSubject(email)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 1000 * 60 * 60 * 24 * 7)) // 7 days
                .signWith(signingKey, SignatureAlgorithm.HS256)
                .compact();
    }

    // Validate JWT Token
    public boolean validateToken(String token, UserDetails userDetails) {
        final String username = extractEmail(token);
        return (username.equals(userDetails.getUsername()) && !isTokenExpired(token));
    }

    private boolean isTokenExpired(String token) {
        final Date expiration = extractAllClaims(token).getExpiration();
        return expiration.before(new Date());
    }

    // Extract Email from JWT Token
    public String extractEmail(String token) {
        return extractAllClaims(token).getSubject();
    }

    // Extract Organisation ID from JWT Token
    public Long extractOrgId(String token) {
        return extractAllClaims(token).get("orgId", Long.class);
    }

    // Extract isSystemAdmin from JWT Token
    public boolean extractIsSystemAdmin(String token) {
        return extractAllClaims(token).get("isSystemAdmin", Boolean.class);
    }

    // Extract chat password
    public String extractChatPassword(String token) {
        return extractAllClaims(token).get("password", String.class);
    }

    // Extract All Claims
    private Claims extractAllClaims(String token) {
        return Jwts.parserBuilder().setSigningKey(signingKey).build().parseClaimsJws(token).getBody();
    }
}
