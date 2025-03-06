package com.ase.angelos_kb_backend.dto;
import java.time.LocalDateTime;
import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@ToString
public class WebsiteResponseDTO {
    private String id;
    private String title;
    private String link;
    private LocalDateTime lastUpdated;
    private List<StudyProgramDTO> studyPrograms;
}
