package com.ase.angelos_kb_backend.dto;

import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class QaLogDTO {
    private String id;
    private LocalDateTime createdAt;
    private String question;
    private String answer;
    private String studyProgram;
    private Long orgId;
}
