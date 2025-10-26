package com.ase.angelos_kb_backend.repository;

import com.ase.angelos_kb_backend.model.QaLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

public interface QaLogRepository extends JpaRepository<QaLog, UUID> {
    List<QaLog> findAllByOrderByCreatedAtDesc();
    List<QaLog> findByOrgIdOrderByCreatedAtDesc(Long orgId);

    long deleteByCreatedAtBefore(LocalDateTime cutoff);
}