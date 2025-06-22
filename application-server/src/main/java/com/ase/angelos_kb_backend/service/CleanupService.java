package com.ase.angelos_kb_backend.service;

import java.time.Instant;
import java.time.temporal.ChronoUnit;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import com.ase.angelos_kb_backend.repository.EventRepository;

@Service
public class CleanupService {
    private final EventRepository eventLogRepository;

    public CleanupService(EventRepository eventLogRepository) {
        this.eventLogRepository = eventLogRepository;
    }

    @Scheduled(cron = "0 15 2 * * ?")
    public void cleanOldEventLogs() {
        Instant cutoff = Instant.now().minus(365, ChronoUnit.DAYS);
        long countBefore = eventLogRepository.count();
        eventLogRepository.deleteByTimestampBefore(cutoff);
        long countAfter = eventLogRepository.count();
        System.out.println("Deleted " + (countBefore - countAfter) + " old event logs.");
    }
}
