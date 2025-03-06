package com.ase.angelos_kb_backend.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import org.springframework.web.multipart.MultipartFile;


@Schema(description = "Upload request containing metadata and a PDF file")
public class DocumentUploadRequestDTO {
    @Schema(description = "Document metadata in JSON format")
    private DocumentRequestDTO documentRequestDTO;

    @Schema(description = "The PDF file to upload", type = "string", format = "binary")
    private MultipartFile file;

    // Getters and Setters
    public DocumentRequestDTO getDocumentRequestDTO() {
        return documentRequestDTO;
    }

    public void setDocumentRequestDTO(DocumentRequestDTO documentRequestDTO) {
        this.documentRequestDTO = documentRequestDTO;
    }

    public MultipartFile getFile() {
        return file;
    }

    public void setFile(MultipartFile file) {
        this.file = file;
    }
}