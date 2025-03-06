package com.ase.angelos_kb_backend.service;

import com.ase.angelos_kb_backend.dto.DocumentDataDTO;
import com.ase.angelos_kb_backend.dto.DocumentRequestDTO;
import com.ase.angelos_kb_backend.exception.ResourceNotFoundException;
import com.ase.angelos_kb_backend.exception.UnauthorizedException;
import com.ase.angelos_kb_backend.model.DocumentContent;
import com.ase.angelos_kb_backend.model.Organisation;
import com.ase.angelos_kb_backend.model.StudyProgram;
import com.ase.angelos_kb_backend.repository.DocumentContentRepository;
import com.ase.angelos_kb_backend.service.DocumentService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class DocumentService {

    private final DocumentContentRepository documentContentRepository;
    private final OrganisationService organisationService;
    private final StudyProgramService studyProgramService;
    private final AngelosService angelosService;
    private final ParsingService parsingService;
    private final FileStorageService fileStorageService;

    public DocumentService(DocumentContentRepository documentContentRepository,
                           OrganisationService organisationService,
                           StudyProgramService studyProgramService,
                           AngelosService angelosService,
                           ParsingService parsingService,
                           FileStorageService fileStorageService) {
        this.documentContentRepository = documentContentRepository;
        this.organisationService = organisationService;
        this.studyProgramService = studyProgramService;
        this.angelosService = angelosService;
        this.parsingService = parsingService;
        this.fileStorageService = fileStorageService;
    }

    /**
     * Get document by ID.
     */
    public DocumentContent getDocumentById(UUID docId, Long orgId) {
        DocumentContent document = documentContentRepository.findById(docId)
                .orElseThrow(() -> new ResourceNotFoundException("Document not found with id " + docId));

        if (!document.getOrganisation().getOrgID().equals(orgId)) {
            throw new UnauthorizedException("You are not authorized to access this document.");
        }

        return document;
    }

    /**
     * Get all documents by organisation ID.
     */
    public List<DocumentDataDTO> getAllDocumentsByOrgId(Long orgId) {
        List<DocumentContent> documents = documentContentRepository.findByOrganisationOrgID(orgId);
        return documents.stream().map(this::convertToDataDto).collect(Collectors.toList());
    }

    /**
     * Edit a document's title and study programs.
     */
    @Transactional
    public DocumentDataDTO editDocument(Long orgId, UUID docId, DocumentRequestDTO documentRequestDTO, MultipartFile file) {
        DocumentContent document = documentContentRepository.findById(docId)
                .orElseThrow(() -> new ResourceNotFoundException("Document not found with id " + docId));

        if (!document.getOrganisation().getOrgID().equals(orgId)) {
            throw new UnauthorizedException("You are not authorized to edit this document.");
        }

        // Update Title
        document.setTitle(documentRequestDTO.getTitle());

        // Update Study Programs
        List<StudyProgram> newStudyPrograms = studyProgramService.getStudyProgramsByIds(documentRequestDTO.getStudyProgramIds());
        document.setStudyPrograms(newStudyPrograms);

        DocumentContent updatedDocument = documentContentRepository.save(document);
        DocumentDataDTO documentDataDTO = convertToDataDto(updatedDocument);

        boolean success = false;
        success = angelosService.sendDocumentEditRequest(documentDataDTO, orgId);

        // If a new file is uploaded, replace the old one
        if (success && file != null && !file.isEmpty()) {
            if (file.getSize() > 5 * 1024 * 1024) { // 5MB limit
                throw new IllegalArgumentException("File size exceeds the maximum allowed size of 5MB.");
            }

            // Delete the old file if it exists
            if (document.getFilename() != null) {
                fileStorageService.deleteFile(document.getFilename());
            }

            String newFilename = UUID.randomUUID().toString() + ".pdf";
            fileStorageService.storeFile(file, newFilename);
            document.setFilename(newFilename);
            document.setOriginalFilename(file.getOriginalFilename());

            String parsedContent = parsingService.parseDocument(file);
            String contentHash = parsingService.computeContentHash(parsedContent);

            if (document.getContentHash() == null || ! contentHash.equals(document.getContentHash())) {
                success = angelosService.sendDocumentRefreshRequest(documentDataDTO.getId(), parsedContent);
                document.setContentHash(contentHash);
            }
        }

        if (!success) {
            throw new RuntimeException("Failed to send update request to Angelos RAG system.");
        }

        return documentDataDTO;
    }

    @Transactional
    public DocumentDataDTO addDocument(Long orgId, DocumentRequestDTO documentRequestDTO, MultipartFile file) {
        Organisation organisation = organisationService.getOrganisationById(orgId);

        if (file.getSize() > 5 * 1024 * 1024) { // 5MB limit
            throw new IllegalArgumentException("File size exceeds the maximum allowed size of 5MB.");
        }

        // Generate a unique filename
        String filename = UUID.randomUUID().toString() + ".pdf";

        try {
            // Store the file in the file system using the unique filename
            fileStorageService.storeFile(file, filename);

            // Create DocumentContent entity
            DocumentContent documentContent = new DocumentContent();
            documentContent.setTitle(documentRequestDTO.getTitle());
            documentContent.setFilename(filename); // Stored filename
            documentContent.setOriginalFilename(file.getOriginalFilename());
            documentContent.setOrganisation(organisation);

            // Fetch and set Study Programs
            List<StudyProgram> studyPrograms = studyProgramService.getStudyProgramsByIds(documentRequestDTO.getStudyProgramIds());
            documentContent.setStudyPrograms(studyPrograms);

            // Save metadata to database
            DocumentContent savedDocument = documentContentRepository.save(documentContent);

            // Map to Response DTO
            DocumentDataDTO dto = convertToDataDto(savedDocument);

            // Parse content and send it to Angelos
            String parsedContent = parsingService.parseDocument(file);
            boolean success = angelosService.sendDocumentAddRequest(dto, parsedContent, orgId);
            if (!success) {
                // If the Angelos request fails, throw an exception to trigger rollback
                throw new RuntimeException("Failed to send add request to Angelos RAG system.");
            }

            return dto;

        } catch (Exception ex) {
            // If an exception occurs, clean up the stored file
            fileStorageService.deleteFile(filename);
            throw ex;
        }
    }

    @Transactional
    public void deleteDocument(Long orgId, UUID docId) {
        // Fetch the document from the database
        DocumentContent document = documentContentRepository.findById(docId)
                .orElseThrow(() -> new ResourceNotFoundException("Document not found with id " + docId));

        // Ensure the document belongs to the given organisation
        if (!document.getOrganisation().getOrgID().equals(orgId)) {
            throw new UnauthorizedException("You are not authorized to delete this document.");
        }

        // Delete the file from the file system
        try {
            fileStorageService.deleteFile(document.getFilename());
        } catch (Exception ex) {
            throw new RuntimeException("Failed to delete the file from the file system.", ex);
        }
        documentContentRepository.delete(document);
    }

    /**
     * Convert DocumentContent to DocumentDataDTO.
     */
    private DocumentDataDTO convertToDataDto(DocumentContent documentContent) {
        return DocumentDataDTO.builder()
            .id(documentContent.getDocID().toString())
            .title(documentContent.getTitle())
            .studyPrograms(
                    documentContent.getStudyPrograms().stream()
                            .map(studyProgramService::convertToDto)
                            .collect(Collectors.toList())
            )
            .createdAt(documentContent.getCreatedAt())
            .updatedAt(documentContent.getUpdatedAt())
            .build();
    }
}