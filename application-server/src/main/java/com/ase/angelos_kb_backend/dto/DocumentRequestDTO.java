package com.ase.angelos_kb_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DocumentRequestDTO {
    @Schema(description = "Title of the document", example = "Sample Document Title")
    private String title;

    @Schema(description = "List of associated study program IDs")
    private List<Long> studyProgramIds;
}