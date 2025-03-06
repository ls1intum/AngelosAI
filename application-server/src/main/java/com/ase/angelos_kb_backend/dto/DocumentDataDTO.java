package com.ase.angelos_kb_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DocumentDataDTO {
    private String id;
    private String title;
    private List<StudyProgramDTO> studyPrograms;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}