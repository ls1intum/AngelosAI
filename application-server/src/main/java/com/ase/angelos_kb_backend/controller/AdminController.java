package com.ase.angelos_kb_backend.controller;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.core.io.support.ResourcePatternResolver;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.ase.angelos_kb_backend.dto.SampleQuestionDTO;
import com.ase.angelos_kb_backend.dto.StudyProgramDTO;
import com.ase.angelos_kb_backend.dto.WebsiteRequestDTO;
import com.ase.angelos_kb_backend.model.Organisation;
import com.ase.angelos_kb_backend.model.StudyProgram;
import com.ase.angelos_kb_backend.service.OrganisationService;
import com.ase.angelos_kb_backend.service.SampleQuestionService;
import com.ase.angelos_kb_backend.service.StudyProgramService;
import com.ase.angelos_kb_backend.service.WebsiteService;
import com.ase.angelos_kb_backend.util.JwtUtil;
import com.ase.angelos_kb_backend.util.SampleQuestionJson;
import com.ase.angelos_kb_backend.util.WebsiteJson;
import com.fasterxml.jackson.databind.ObjectMapper;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    private final OrganisationService organisationService;
    private final SampleQuestionService sampleQuestionService;
    private final WebsiteService websiteService;
    private final StudyProgramService studyProgramService;
    private final JwtUtil jwtUtil;

    public AdminController(OrganisationService organisationService, SampleQuestionService sampleQuestionService, JwtUtil jwtUtil, 
            WebsiteService websiteService, StudyProgramService studyProgramService) {
        this.organisationService = organisationService;
        this.jwtUtil = jwtUtil;
        this.studyProgramService = studyProgramService;
        this.sampleQuestionService = sampleQuestionService;
        this.websiteService = websiteService;
    }

    @PostMapping("/init-db")
    public ResponseEntity<Void> initDatabaseForOrg(
            @RequestHeader("Authorization") String token,
            @RequestParam Long orgId,
            @RequestParam boolean isCITAdvising) {
        
        // Ensure system admin privilege
        if (!jwtUtil.extractIsSystemAdmin(token.replace("Bearer ", ""))) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }

        // Check if organisation exists
        Organisation organisation = organisationService.getOrganisationById(orgId);
        if (organisation == null) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(null);
        }

        try {
            // Parse sample questions if 
            List<SampleQuestionDTO> sampleQuestionDTOs = new ArrayList<>();
            if (isCITAdvising) {
                sampleQuestionDTOs = loadSampleQuestionsFromResources(orgId);
            }
            System.out.println(sampleQuestionDTOs.size() + " sample question objects parsed.");
            // Parse websites
            List<WebsiteRequestDTO> websiteRequestDTOs = loadWebsitesFromResources(orgId, isCITAdvising);
            System.out.println(websiteRequestDTOs.size() + " websites objects parsed.");

            // Save to DB and push to RAG
            if (!websiteRequestDTOs.isEmpty()) {
                websiteService.addWebsitesInBatch(orgId, websiteRequestDTOs);
            }

            if (!sampleQuestionDTOs.isEmpty()) {
                sampleQuestionService.addSampleQuestions(orgId, sampleQuestionDTOs);
            }

            return ResponseEntity.ok().build();

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    private List<SampleQuestionDTO> loadSampleQuestionsFromResources(Long orgId) throws IOException {
        List<SampleQuestionDTO> result = new ArrayList<>();
        ResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
        Resource[] resources = resolver.getResources("classpath:db-init/sample-questions/*.json");
        System.out.println(resources.length + " sample question resources found.");

        int numberOfOrgPrograms = organisationService.getOrganisationById(orgId).getStudyPrograms().size();

        for (Resource resource : resources) {
            SampleQuestionJson sqJson = new ObjectMapper().readValue(resource.getInputStream(), SampleQuestionJson.class);
            
            // Process study program
            List<StudyProgramDTO> studyProgramDTOs = resolveStudyPrograms(orgId, numberOfOrgPrograms, sqJson.getStudyProgram());
            if (studyProgramDTOs == null) {
                // Means study program not found or doesn't belong to org; skip
                continue;
            }

            // Handle wrongly formatted input JSONs (trailing quote)
            String question = sqJson.getQuestion();
            question = (question != null && question.endsWith("\"")) ? question.substring(0, question.length() - 1) : question;
            
            SampleQuestionDTO dto = new SampleQuestionDTO();
            dto.setId(null); // ID will be assigned on save
            dto.setTopic(sqJson.getTopic());
            dto.setQuestion(question);
            dto.setAnswer(sqJson.getAnswer());
            dto.setStudyPrograms(studyProgramDTOs);
            
            result.add(dto);
        }

        return result;
    }

    private List<WebsiteRequestDTO> loadWebsitesFromResources(Long orgId, boolean includeCIT) throws IOException {
        Map<String, List<Long>> websiteMap = new HashMap<>();
        ResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
        Resource[] resources = resolver.getResources("classpath:db-init/websites/*.json");
        ObjectMapper objectMapper = new ObjectMapper();
        System.out.println(resources.length + " website resources found.");

        int numberOfOrgPrograms = organisationService.getOrganisationById(orgId).getStudyPrograms().size();

        for (Resource resource : resources) {
            WebsiteJson wJson = objectMapper.readValue(resource.getInputStream(), WebsiteJson.class);

            // Process study program
            List<StudyProgramDTO> studyProgramDTOs = resolveStudyPrograms(orgId, numberOfOrgPrograms, wJson.getStudyProgram());
            if (studyProgramDTOs == null) {
                // Skip if study program is invalid or belongs to another org
                continue;
            }
            // Skip general CIT websites if organisation is not CIT academic advising
            if (studyProgramDTOs.isEmpty() && (wJson.getLink().contains("cit.tum.de") && !includeCIT)) {
                continue;
            }

            // Convert StudyProgramDTO list to IDs
            List<Long> spIds = studyProgramDTOs.stream()
                    .map(StudyProgramDTO::getId)
                    .collect(Collectors.toList());

            // Create a key from link and title
            // Using link+title as a combined key, or you might prefer a structured key object
            String key = wJson.getLink() + "###" + wJson.getTitle();

            // Add or merge study program IDs
            websiteMap.computeIfAbsent(key, k -> new ArrayList<>()).addAll(spIds);
        }

        // Now convert the map to a list of WebsiteRequestDTO
        List<WebsiteRequestDTO> result = new ArrayList<>();
        for (Map.Entry<String, List<Long>> entry : websiteMap.entrySet()) {
            String[] parts = entry.getKey().split("###");
            if (parts.length < 2) {
                continue;
            }
            String link = parts[0];
            String title = parts[1];

            WebsiteRequestDTO dto = new WebsiteRequestDTO();
            dto.setTitle(title);
            dto.setLink(link);

            List<Long> uniqueSpIds = entry.getValue().stream().distinct().collect(Collectors.toList());
            dto.setStudyProgramIds(uniqueSpIds);

            result.add(dto);
        }

        return result;
    }

    /**
     * Resolves the study programs from the given string.
     * Returns:
     * - Empty list if "general" or all study programs of org
     * - A single-element list if found
     * - null if not found or doesn't belong to given org
     */
    private List<StudyProgramDTO> resolveStudyPrograms(Long orgId, int numberOfOrgPrograms, String programSlug) {
        // Handling of general information
        if ("general".equalsIgnoreCase(programSlug)) {
            return Collections.emptyList();
        }
        String name = convertSlugToName(programSlug);

        List<StudyProgram> sps = studyProgramService.getStudyProgramsByName(name);
        if (sps == null || sps.isEmpty()) {
            return null;
        }

        // Ensure correct organisation
        List<StudyProgram> filtered = sps.stream()
                .filter(sp -> sp.getOrganisation() != null && sp.getOrganisation().getOrgID().equals(orgId))
                .collect(Collectors.toList());
        if (filtered.isEmpty()) {
            return null;
        }
        // Handling of information concerning every study program
        if (numberOfOrgPrograms == filtered.size()) {
            return Collections.emptyList();
        }

        return filtered.stream()
                .map(sp -> {
                    StudyProgramDTO spDto = new StudyProgramDTO();
                    spDto.setId(sp.getSpID());
                    spDto.setName(sp.getName());
                    return spDto;
                })
                .collect(Collectors.toList());
    }

    private String convertSlugToName(String slug) {
        // Split by "-"
        String[] parts = slug.split("-");
        // Capitalize first letter of each part and join by space
        return Arrays.stream(parts)
                .map(part -> part.substring(0,1).toUpperCase() + part.substring(1))
                .collect(Collectors.joining(" "));
    }
}
