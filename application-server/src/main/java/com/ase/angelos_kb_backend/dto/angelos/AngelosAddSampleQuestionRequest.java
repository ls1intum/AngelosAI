package com.ase.angelos_kb_backend.dto.angelos;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AngelosAddSampleQuestionRequest {
    private String id;
    private String question;
    private String answer;
    private String topic;
    private List<String> studyPrograms;
    private Long orgId;
}