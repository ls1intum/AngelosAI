package com.ase.angelos_kb_backend.controller;

import java.net.MalformedURLException;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;

import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.ase.angelos_kb_backend.dto.DocumentDataDTO;
import com.ase.angelos_kb_backend.dto.DocumentRequestDTO;
import com.ase.angelos_kb_backend.dto.DocumentUploadRequestDTO;
import com.ase.angelos_kb_backend.model.DocumentContent;
import com.ase.angelos_kb_backend.service.DocumentService;
import com.ase.angelos_kb_backend.service.FileStorageService;
import com.ase.angelos_kb_backend.util.JwtUtil;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Encoding;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.parameters.RequestBody;
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    private final DocumentService documentService;
    private final FileStorageService fileStorageService;
    private final JwtUtil jwtUtil;

    public DocumentController(DocumentService documentService, FileStorageService fileStorageService, JwtUtil jwtUtil) {
        this.documentService = documentService;
        this.fileStorageService = fileStorageService;
        this.jwtUtil = jwtUtil;
    }

    /**
     * Get all documents by organisation ID.
     */
    @GetMapping
    public ResponseEntity<List<DocumentDataDTO>> getAllDocuments(@RequestHeader("Authorization") String token) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        List<DocumentDataDTO> documents = documentService.getAllDocumentsByOrgId(orgId);
        return ResponseEntity.ok(documents);
    }

    /**
     * Edit a document's title and study programs.
     */
    @SuppressWarnings("null")
    @PutMapping(value = "/{docId}", consumes = MediaType.MULTIPART_FORM_DATA_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(
        summary = "Edit a document",
        description = "Updates a document's metadata and optionally its file",
        requestBody = @RequestBody(
            required = true,
            content = {
                @Content(
                    mediaType = MediaType.MULTIPART_FORM_DATA_VALUE,
                    schema = @Schema(implementation = DocumentUploadRequestDTO.class),
                    encoding = {
                        @Encoding(name = "documentRequestDTO", contentType = MediaType.APPLICATION_JSON_VALUE),
                        @Encoding(name = "file", contentType = "application/pdf")
                    }
                )
            }
        )
    )
    public ResponseEntity<DocumentDataDTO> editDocument(
            @RequestHeader("Authorization") String token,
            @PathVariable UUID docId,
            @Valid @RequestPart("documentRequestDTO") DocumentRequestDTO documentRequestDTO,
            @RequestPart(value = "file", required = false) MultipartFile file) {

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));

        if (file != null && file.getContentType() != null && !file.getContentType().equals("application/pdf")) {
            return ResponseEntity.status(HttpStatus.UNSUPPORTED_MEDIA_TYPE)
                    .body(null);
        }

        DocumentDataDTO updatedDocument = documentService.editDocument(orgId, docId, documentRequestDTO, file);

        return ResponseEntity.ok(updatedDocument);
    }

    
    @SuppressWarnings("null")
    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(
        summary = "Upload a PDF document",
        description = "Adds a new document with JSON metadata and a PDF file",
        requestBody = @RequestBody(
            required = true,
            content = {
                @Content(
                    mediaType = MediaType.MULTIPART_FORM_DATA_VALUE,
                    schema = @Schema(implementation = DocumentUploadRequestDTO.class),
                    encoding = {
                        @Encoding(name = "documentRequestDTO", contentType = MediaType.APPLICATION_JSON_VALUE),
                        @Encoding(name = "file", contentType = "application/pdf")
                    }
                )
            }
        )
    )
    public ResponseEntity<DocumentDataDTO> addDocument(
            @RequestHeader("Authorization") String token,
            @Valid @RequestPart("documentRequestDTO") DocumentRequestDTO documentRequestDTO,
            @RequestPart("file") MultipartFile file) {

        // Validate that the uploaded file is a PDF
        if (file == null || file.getContentType() == null || !file.getContentType().equals("application/pdf")) {
            return ResponseEntity.status(HttpStatus.UNSUPPORTED_MEDIA_TYPE)
                    .body(null);
        }

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));

        // Add document (file and metadata)
        DocumentDataDTO responseDTO = documentService.addDocument(orgId, documentRequestDTO, file);

        return ResponseEntity.ok(responseDTO);
    }

    @GetMapping("/{docId}/download")
    public ResponseEntity<Resource> downloadDocument(
            @RequestHeader("Authorization") String token,
            @PathVariable UUID docId) {

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        DocumentContent document = documentService.getDocumentById(docId, orgId);

        // Load file as a resource
        Path filePath = fileStorageService.loadFile(document.getFilename());
        Resource resource;
        try {
            resource = new UrlResource(filePath.toUri());
            if (!resource.exists() || !resource.isReadable()) {
                throw new RuntimeException("File not found or not readable");
            }
        } catch (MalformedURLException e) {
            throw new RuntimeException("File not found or not readable");
        }

        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_PDF)
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + document.getOriginalFilename() + "\"")
                .body(resource);
    }

    @DeleteMapping("/{docId}")
    public ResponseEntity<Void> deleteDocument(
            @RequestHeader("Authorization") String token,
            @PathVariable UUID docId) {

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        documentService.deleteDocument(orgId, docId);

        return ResponseEntity.noContent().build();
    }
}
