package com.ase.angelos_kb_backend.dto.angelos;

import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AngelosChatRequest {
    List<AngelosChatMessage> messages;
    String study_program;
    Long orgId;
}

