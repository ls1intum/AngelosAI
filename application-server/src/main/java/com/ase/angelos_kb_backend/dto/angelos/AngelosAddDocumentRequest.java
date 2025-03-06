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
public class AngelosAddDocumentRequest {
    private String id;
    private String title;
    private List<String> studyPrograms;
    private String content;
    private Long orgId;
}