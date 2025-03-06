package com.ase.angelos_kb_backend.service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.ase.angelos_kb_backend.dto.StudyProgramDTO;
import com.ase.angelos_kb_backend.dto.WebsiteRequestDTO;
import com.ase.angelos_kb_backend.dto.WebsiteResponseDTO;
import com.ase.angelos_kb_backend.dto.angelos.AngelosAddWebsiteRequest;
import com.ase.angelos_kb_backend.exception.ResourceNotFoundException;
import com.ase.angelos_kb_backend.exception.UnauthorizedException;
import com.ase.angelos_kb_backend.model.Organisation;
import com.ase.angelos_kb_backend.model.StudyProgram;
import com.ase.angelos_kb_backend.model.WebsiteContent;
import com.ase.angelos_kb_backend.repository.WebsiteContentRepository;
import com.ase.angelos_kb_backend.util.ParseResult;


@Service
public class WebsiteService {

    private final WebsiteContentRepository websiteContentRepository;
    private final OrganisationService organisationService;
    private final StudyProgramService studyProgramService;
    private final AngelosService angelosService;
    private final ParsingService parsingService;

    public WebsiteService(WebsiteContentRepository websiteContentRepository,
                          OrganisationService organisationService,
                          StudyProgramService studyProgramService,
                          AngelosService angelosService,
                          ParsingService parsingService) {
        this.websiteContentRepository = websiteContentRepository;
        this.organisationService = organisationService;
        this.studyProgramService = studyProgramService;
        this.angelosService = angelosService;
        this.parsingService = parsingService;
    }

    public List<WebsiteResponseDTO> getAllWebsitesByOrgId(Long orgId) {
        List<WebsiteContent> websites = websiteContentRepository.findByOrganisationOrgID(orgId);
        return websites.stream().map(this::convertToDto).collect(Collectors.toList());
    }

    public WebsiteResponseDTO getWebsiteById(UUID id) {
        WebsiteContent websiteContent = websiteContentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Website not found with id " + id));
        return this.convertToDto(websiteContent);
    }

    @Transactional
    public WebsiteResponseDTO addWebsite(Long orgId, WebsiteRequestDTO websiteRequestDTO) {
        // Fetch Organisation
        Organisation organisation = organisationService.getOrganisationById(orgId);

        Map<Long, String> studyProgramIdToNameMap = studyProgramService.getStudyProgramsByIds(websiteRequestDTO.getStudyProgramIds()).stream()
            .collect(Collectors.toMap(StudyProgram::getSpID, StudyProgram::getName));

        // Map DTO to Entity
        WebsiteContent websiteContent = new WebsiteContent();
        websiteContent.setTitle(websiteRequestDTO.getTitle());
        websiteContent.setLink(websiteRequestDTO.getLink());
        websiteContent.setOrganisation(organisation);

        // Fetch Study Programs
        List<StudyProgram> studyPrograms = studyProgramService.getStudyProgramsByIds(websiteRequestDTO.getStudyProgramIds());
        websiteContent.setStudyPrograms(studyPrograms);

        // Parse website content
        ParseResult parseResult = parsingService.parseWebsite(websiteContent.getLink());
        String parsedContent = parseResult.getContent();
        String websiteType = parseResult.getParserType();

        // Compute content hash
        String contentHash = parsingService.computeContentHash(parsedContent);
        websiteContent.setContentHash(contentHash);

        // Save to database
        WebsiteContent savedWebsite = websiteContentRepository.save(websiteContent);
        // Prepare Angelos RAG Request
        AngelosAddWebsiteRequest ragRequest = new AngelosAddWebsiteRequest();
        ragRequest.setId(savedWebsite.getId().toString());
        ragRequest.setOrgId(orgId);
        ragRequest.setTitle(websiteRequestDTO.getTitle());
        ragRequest.setLink(websiteRequestDTO.getLink());
        // Map IDs to Names
        List<String> studyProgramNames = websiteRequestDTO.getStudyProgramIds().stream()
            .map(studyProgramIdToNameMap::get)
            .toList();
        ragRequest.setStudyPrograms(studyProgramNames);
        ragRequest.setContent(parsedContent);
        ragRequest.setType(websiteType);

        // Send add request to Angelos RAG
        boolean success = angelosService.sendWebsiteAddRequest(ragRequest);

        if (!success) {
            throw new RuntimeException("Failed to send add request to Angelos RAG system.");
        }

        // Map Entity to Response DTO
        return convertToDto(savedWebsite);
    }

    @Transactional
    public List<WebsiteResponseDTO> addWebsitesInBatch(Long orgId, List<WebsiteRequestDTO> websiteRequestDTOs) {
        Organisation organisation = organisationService.getOrganisationById(orgId);
        List<WebsiteResponseDTO> responseDTOs = new ArrayList<>();

        // Gather all unique study program IDs from all websites
        List<Long> allStudyProgramIds = websiteRequestDTOs.stream()
            .flatMap(dto -> dto.getStudyProgramIds().stream())
            .distinct()
            .toList();

        // Fetch all StudyPrograms in bulk
        Map<Long, String> studyProgramIdToNameMap = studyProgramService.getStudyProgramsByIds(allStudyProgramIds).stream()
            .collect(Collectors.toMap(StudyProgram::getSpID, StudyProgram::getName));

        int batchSize = 100;
        int totalWebsites = websiteRequestDTOs.size();
        
        for (int i = 0; i < totalWebsites; i += batchSize) {
            List<WebsiteRequestDTO> batch = websiteRequestDTOs.subList(i, Math.min(i + batchSize, totalWebsites));
            List<AngelosAddWebsiteRequest> ragRequests = new ArrayList<>();

            for (WebsiteRequestDTO dto : batch) {
                WebsiteContent websiteContent = new WebsiteContent();
                websiteContent.setTitle(dto.getTitle());
                websiteContent.setLink(dto.getLink());
                websiteContent.setOrganisation(organisation);

                // Fetch Study Programs
                List<StudyProgram> studyPrograms = studyProgramService.getStudyProgramsByIds(dto.getStudyProgramIds());
                websiteContent.setStudyPrograms(studyPrograms);

                // Parse website content
                ParseResult parseResult = parsingService.parseWebsite(websiteContent.getLink());
                String parsedContent = parseResult.getContent();
                String websiteType = parseResult.getParserType();

                // Compute content hash
                String contentHash = parsingService.computeContentHash(parsedContent);
                websiteContent.setContentHash(contentHash);

                // Save to database
                WebsiteContent savedWebsite = websiteContentRepository.save(websiteContent);
                responseDTOs.add(convertToDto(savedWebsite));

                // Prepare Angelos RAG Request
                AngelosAddWebsiteRequest ragRequest = new AngelosAddWebsiteRequest();
                ragRequest.setId(savedWebsite.getId().toString());
                ragRequest.setOrgId(orgId);
                ragRequest.setTitle(dto.getTitle());
                ragRequest.setLink(dto.getLink());
                // Map IDs to Names
                List<String> studyProgramNames = dto.getStudyProgramIds().stream()
                    .map(studyProgramIdToNameMap::get)
                    .toList();
                ragRequest.setStudyPrograms(studyProgramNames);
                ragRequest.setContent(parsedContent);
                ragRequest.setType(websiteType);

                ragRequests.add(ragRequest);
            }

            // Send batch to RAG
            boolean success = angelosService.sendBatchWebsiteAddRequest(ragRequests);

            if (!success) {
                throw new RuntimeException("Failed to send batch add request to Angelos RAG system.");
            }
        }

        return responseDTOs;
    }

    @Transactional
    public WebsiteResponseDTO editWebsite(Long orgId, UUID websiteId, WebsiteRequestDTO websiteRequestDTO) {
        // Fetch the existing WebsiteContent by ID
        WebsiteContent existingWebsite = websiteContentRepository.findById(websiteId)
                .orElseThrow(() -> new ResourceNotFoundException("Website not found with id " + websiteId));
    
        // Ensure the website belongs to the organisation
        if (!existingWebsite.getOrganisation().getOrgID().equals(orgId)) {
            throw new UnauthorizedException("You are not authorized to edit this website.");
        }

        String existingTitle = existingWebsite.getTitle();
        existingWebsite.setTitle(websiteRequestDTO.getTitle());

        List<StudyProgram> newStudyPrograms = studyProgramService.getStudyProgramsByIds(websiteRequestDTO.getStudyProgramIds());

        // Compare existing and new StudyProgram IDs
        Set<Long> existingStudyProgramIds = existingWebsite.getStudyPrograms().stream().map(StudyProgram::getSpID).collect(Collectors.toSet());
        Set<Long> newStudyProgramIds = newStudyPrograms.stream().map(StudyProgram::getSpID).collect(Collectors.toSet());

        if (!existingTitle.equals(websiteRequestDTO.getTitle()) || !existingStudyProgramIds.equals(newStudyProgramIds)) {
            List<Long> spList = new ArrayList<Long>(newStudyProgramIds);
            List<String> studyProgramNames = studyProgramService.getStudyProgramsByIds(spList).stream()
                .map(StudyProgram::getName)
                .collect(Collectors.toList());

            // Convert StudyProgram entities to DTOs
            boolean success = angelosService.sendWebsiteUpdateRequest(websiteId.toString(), websiteRequestDTO.getTitle(), studyProgramNames, orgId);
            if (!success) {
                throw new RuntimeException("Failed to send update request to Angelos RAG system.");
            }
            existingWebsite.setStudyPrograms(newStudyPrograms);
        }
    
        // Parse website content
        String parsedContent = parsingService.parseWebsite(existingWebsite.getLink()).getContent();

        // Compute content hash
        String contentHash = parsingService.computeContentHash(parsedContent);
                    
        // Check if content has actually changed
        if (!contentHash.equals(existingWebsite.getContentHash())) {
            // Content has changed, send update request to Angelos RAG
            boolean success = angelosService.sendWebsiteRefreshRequest(existingWebsite.getId().toString(), parsedContent);
            if (!success) {
                throw new RuntimeException("Failed to send update request to Angelos RAG system.");
            }
            existingWebsite.setContentHash(contentHash);
        }
        // Save the updated entity to the database
        WebsiteContent updatedWebsite = websiteContentRepository.save(existingWebsite);
    
        // Map Entity to Response DTO
        return convertToDto(updatedWebsite);
    }

    public void deleteWebsite(UUID id, Long orgId) {
        if (websiteContentRepository.existsById(id)) {
            WebsiteContent existingWebsite = websiteContentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Website not found with id " + id));
            if (!existingWebsite.getOrganisation().getOrgID().equals(orgId)) {
                throw new UnauthorizedException("You are not authorized to edit this website.");
            } else {
                boolean success = angelosService.sendWebsiteDeleteRequest(id.toString());
                if (!success) {
                    throw new RuntimeException("Delete request to Angelos RAG system failed.");
                }
                websiteContentRepository.deleteById(id);
            }
        } else {
            throw new ResourceNotFoundException("Website not found with id " + id);
        }
    }

    public WebsiteResponseDTO convertToDto(WebsiteContent websiteContent) {
        WebsiteResponseDTO dto = new WebsiteResponseDTO();
        dto.setId(websiteContent.getId().toString());
        dto.setTitle(websiteContent.getTitle());
        dto.setLink(websiteContent.getLink());
        dto.setLastUpdated(websiteContent.getUpdatedAt());

        // Map study programs to DTOs (assuming StudyProgramDTO and conversion exist)
        List<StudyProgramDTO> studyProgramDTOs = websiteContent.getStudyPrograms().stream()
                .map(sp -> new StudyProgramDTO(sp.getSpID(), sp.getName()))
                .collect(Collectors.toList());
        dto.setStudyPrograms(studyProgramDTOs);

        return dto;
    }
}
