package com.ase.angelos_kb_backend.dto.angelos;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AngelosChatMessage {
    String message;
    String type;
}
