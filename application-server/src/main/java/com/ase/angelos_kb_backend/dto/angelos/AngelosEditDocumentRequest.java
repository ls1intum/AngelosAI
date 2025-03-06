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
public class AngelosEditDocumentRequest {
    private Long orgId;
    private String title;
    private List<String> studyPrograms;
}
