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
public class AngelosAddWebsiteRequest {
    private String id;
    private String title;
    private String link;
    private List<String> studyPrograms;
    private String content;
    private String type;
    private Long orgId;
}
