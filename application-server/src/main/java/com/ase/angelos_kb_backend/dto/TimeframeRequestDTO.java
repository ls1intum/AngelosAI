package com.ase.angelos_kb_backend.dto;

import java.time.Instant;
import lombok.Data;

@Data
public class TimeframeRequestDTO {
    private Instant from;
    private Instant to;
}
