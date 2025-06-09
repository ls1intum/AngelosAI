package com.ase.angelos_kb_backend.repository;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

import com.ase.angelos_kb_backend.model.EventLog;

public interface EventRepository extends JpaRepository<EventLog, UUID> {
    List<EventLog> findByOrganisationOrgIDAndTimestampBetween(Long orgId, Instant from, Instant to);
}
