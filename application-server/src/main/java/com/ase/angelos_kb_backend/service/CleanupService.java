package com.ase.angelos_kb_backend.service;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.ase.angelos_kb_backend.repository.EventRepository;
import com.ase.angelos_kb_backend.repository.QaLogRepository;


@Service
public class CleanupService {
    private final EventRepository eventLogRepository;
    private final QaLogRepository qaLogRepository;

    public CleanupService(EventRepository eventLogRepository, QaLogRepository qaLogRepository) {
        this.eventLogRepository = eventLogRepository;
        this.qaLogRepository = qaLogRepository;
    }

    @Scheduled(cron = "0 15 2 * * ?")
    @Transactional
    public void cleanOldEventLogs() {
        Instant cutoff = Instant.now().minus(365, ChronoUnit.DAYS);
        long countBefore = eventLogRepository.count();
        eventLogRepository.deleteByTimestampBefore(cutoff);
        long countAfter = eventLogRepository.count();
        System.out.println("Deleted " + (countBefore - countAfter) + " old event logs.");
    }

    @Scheduled(cron = "0 10 3 * * ?")
    @Transactional
    public void cleanOldQaLogs() {
        LocalDateTime cutoff = LocalDateTime.now().minus(30, ChronoUnit.DAYS);
        long deleted = qaLogRepository.deleteByCreatedAtBefore(cutoff);
        System.out.println("Deleted " + deleted + " old QA logs (older than 30 days).");
    }
}
