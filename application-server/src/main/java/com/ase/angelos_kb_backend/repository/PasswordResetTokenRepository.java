package com.ase.angelos_kb_backend.repository;

import com.ase.angelos_kb_backend.model.PasswordResetToken;
import com.ase.angelos_kb_backend.model.User;

import org.springframework.data.jpa.repository.JpaRepository;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

public interface PasswordResetTokenRepository extends JpaRepository<PasswordResetToken, UUID> {
    Optional<PasswordResetToken> findByTokenAndUsedIsFalseAndExpiresAtAfter(String token, Instant now);
    void deleteByExpiresAtBefore(Instant cutoff);
    void deleteAllByUser(User user);
    int countByUser(User user);
}