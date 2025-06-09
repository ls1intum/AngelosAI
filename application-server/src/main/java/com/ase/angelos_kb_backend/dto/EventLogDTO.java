package com.ase.angelos_kb_backend.dto;

import java.time.Instant;
import java.util.UUID;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class EventLogDTO {
    private UUID id;
    private Instant timestamp;
    private String eventType;
    private String metadata;
}
