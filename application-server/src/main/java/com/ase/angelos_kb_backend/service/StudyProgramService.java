package com.ase.angelos_kb_backend.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.ase.angelos_kb_backend.dto.StudyProgramDTO;
import com.ase.angelos_kb_backend.exception.ResourceNotFoundException;
import com.ase.angelos_kb_backend.exception.UnauthorizedException;
import com.ase.angelos_kb_backend.model.DocumentContent;
import com.ase.angelos_kb_backend.model.Organisation;
import com.ase.angelos_kb_backend.model.SampleQuestion;
import com.ase.angelos_kb_backend.model.StudyProgram;
import com.ase.angelos_kb_backend.model.WebsiteContent;
import com.ase.angelos_kb_backend.repository.DocumentContentRepository;
import com.ase.angelos_kb_backend.repository.OrganisationRepository;
import com.ase.angelos_kb_backend.repository.SampleQuestionRepository;
import com.ase.angelos_kb_backend.repository.StudyProgramRepository;
import com.ase.angelos_kb_backend.repository.WebsiteContentRepository;


@Service
public class StudyProgramService {
    private final StudyProgramRepository studyProgramRepository;
    private final OrganisationRepository organisationRepository;
    private final OrganisationService organisationService;
    private final SampleQuestionRepository sampleQuestionRepository;
    private final WebsiteContentRepository websiteContentRepository;
    private final DocumentContentRepository documentContentRepository;
    private final AngelosService angelosService;

    public StudyProgramService(
            StudyProgramRepository studyProgramRepository, 
            OrganisationRepository organisationRepository, 
            OrganisationService organisationService,
            SampleQuestionRepository sampleQuestionRepository,
            WebsiteContentRepository websiteContentRepository,
            DocumentContentRepository documentContentRepository,
            AngelosService angelosService
    ) {
        this.studyProgramRepository = studyProgramRepository;
        this.organisationRepository = organisationRepository;
        this.organisationService = organisationService;
        this.sampleQuestionRepository = sampleQuestionRepository;
        this.websiteContentRepository = websiteContentRepository;
        this.documentContentRepository = documentContentRepository;
        this.angelosService = angelosService;
    }

    public List<StudyProgramDTO> getAllStudyProgramsByOrgId(Long orgId) {
        // Check if the organization is "System Organisation"
        Organisation organisation = organisationService.getOrganisationById(orgId);
        if ("System Organisation".equals(organisation.getName())) {
            // Fetch all study programs if the organization is "System Organisation"
            return studyProgramRepository.findAll().stream().map(this::convertToDto).collect(Collectors.toList());
        }
        // Otherwise, filter by organization ID
        return studyProgramRepository.findByOrganisationOrgID(orgId).stream().map(this::convertToDto).collect(Collectors.toList());
    }

    public List<StudyProgramDTO> getAllStudyPrograms() {
        return studyProgramRepository.findAll().stream().map(this::convertToDto).collect(Collectors.toList());
    }

    @Transactional
    public void addStudyProgramToOrg(Long spId, Long orgId) {
        Organisation organisation = organisationRepository.findById(orgId)
                .orElseThrow(() -> new ResourceNotFoundException("Organisation not found with id " + orgId));

        StudyProgram studyProgram = studyProgramRepository.findById(spId)
                .orElseThrow(() -> new ResourceNotFoundException("Study Program not found with id " + spId));

        organisation.getStudyPrograms().add(studyProgram);
        organisationRepository.save(organisation);
    }

    @Transactional
    public void removeStudyProgramFromOrg(Long spId, Long orgId) {
        Organisation organisation = organisationRepository.findById(orgId)
                .orElseThrow(() -> new ResourceNotFoundException("Organisation not found with id " + orgId));

        StudyProgram studyProgram = studyProgramRepository.findById(spId)
                .orElseThrow(() -> new ResourceNotFoundException("Study Program not found with id " + spId));

        organisation.getStudyPrograms().remove(studyProgram);
        organisationRepository.save(organisation);
    }

    @Transactional
    public StudyProgramDTO createStudyProgram(String studyProgramName, Long orgId) {
        // Fetch the Organisation
        Organisation organisation = organisationRepository.findById(orgId)
                .orElseThrow(() -> new ResourceNotFoundException("Organisation not found with id " + orgId));

        // Check if the study program already exists for the organisation
        boolean exists = studyProgramRepository.existsByNameAndOrganisation(studyProgramName, organisation.getOrgID());
        if (exists) {
            throw new IllegalArgumentException("Study program with the name '" + studyProgramName + "' already exists for this organisation.");
        }

        // Create a new StudyProgram
        StudyProgram newStudyProgram = new StudyProgram();
        newStudyProgram.setName(studyProgramName);
        newStudyProgram.setOrganisation(organisation); // Set the owning Organisation

        // Save the StudyProgram
        StudyProgram savedStudyProgram = studyProgramRepository.save(newStudyProgram);

        // Optional: Add the study program to the organisation's list of study programs
        organisation.getStudyPrograms().add(savedStudyProgram);

        return convertToDto(savedStudyProgram);
    }

    public List<StudyProgram> getStudyProgramsByName(String name) {
        return studyProgramRepository.findByName(name);
    }

    @Transactional
    public void deleteStudyProgram(Long id, Long orgId) {
        StudyProgram studyProgram = studyProgramRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Study program not found with id " + id));

        Organisation organisation = organisationService.getOrganisationById(orgId);

        // Ensure user has permission to delete the program
        if (!studyProgram.getOrganisation().getOrgID().equals(orgId)
                && !"System Organisation".equals(organisation.getName())) {
            throw new UnauthorizedException("You are not authorized to delete this study program.");
        }

        // Update resources
        List<WebsiteContent> websitesToUpdate = websiteContentRepository.findByStudyProgramsContains(studyProgram)
                .stream()
                .filter(w -> w.getStudyPrograms().size() > 1)
                .toList();
         List<SampleQuestion> questionsToUpdate = sampleQuestionRepository.findByStudyProgramsContains(studyProgram)
                .stream()
                .filter(q -> q.getStudyPrograms().size() > 1)
                .toList();
        List<DocumentContent> documentsToUpdate = documentContentRepository.findByStudyProgramsContains(studyProgram)
                .stream()
                .filter(d -> d.getStudyPrograms().size() > 1)
                .toList();
        
        // Remove study program reference
        for (WebsiteContent website : websitesToUpdate) {
            website.getStudyPrograms().remove(studyProgram);
            websiteContentRepository.save(website);
        }
        for (SampleQuestion question : questionsToUpdate) {
            question.getStudyPrograms().remove(studyProgram);
            sampleQuestionRepository.save(question);
        }
        for (DocumentContent document : documentsToUpdate) {
            document.getStudyPrograms().remove(studyProgram);
            documentContentRepository.save(document);
        }

        // Delete resources
        List<WebsiteContent> websitesToDelete = websiteContentRepository.findByStudyProgramsContainsOnly(studyProgram);
        List<SampleQuestion> questionsToDelete = sampleQuestionRepository.findByStudyProgramsContainsOnly(studyProgram);
        List<DocumentContent> documentsToDelete = documentContentRepository.findByStudyProgramsContainsOnly(studyProgram);

        websiteContentRepository.deleteAll(websitesToDelete);
        sampleQuestionRepository.deleteAll(questionsToDelete);
        documentContentRepository.deleteAll(documentsToDelete);

        studyProgramRepository.delete(studyProgram);
        
        // Make Angelos requests at the end to make sure that changes are reverted in case of failure
        boolean success = angelosService.sendWebsiteBatchDeleteRequest(websitesToDelete.stream().map(w -> w.getId().toString()).toList());
        if (!success) {
            throw new RuntimeException("Failed to batch delete websites from Angelos RAG system.");
        }
        success = angelosService.sendSampleQuestionBatchDeleteRequest(questionsToDelete.stream().map(w -> w.getSqID().toString()).toList());
        if (!success) {
            throw new RuntimeException("Failed to batch delete sample questions from Angelos RAG system.");
        }
        success = angelosService.sendDocumentBatchDeleteRequest(documentsToDelete.stream().map(w -> w.getDocID().toString()).toList());
        if (!success) {
            throw new RuntimeException("Failed to batch delete documents from Angelos RAG system.");
        }
    }
    /**
     * Fetch a list of StudyPrograms by their IDs.
     * 
     * @param ids List of StudyProgram IDs.
     * @return List of StudyProgram entities.
     * @throws ResourceNotFoundException if any StudyProgram ID is not found.
     */
    public List<StudyProgram> getStudyProgramsByIds(List<Long> ids) {
        // Fetch all StudyPrograms matching the IDs
        List<StudyProgram> studyPrograms = studyProgramRepository.findAllById(ids);

        // Ensure all IDs are valid
        if (studyPrograms.size() != ids.size()) {
            List<Long> foundIds = studyPrograms.stream()
                                               .map(StudyProgram::getSpID)
                                               .toList();
            List<Long> missingIds = ids.stream()
                                       .filter(id -> !foundIds.contains(id))
                                       .toList();
            throw new ResourceNotFoundException("StudyProgram(s) not found for IDs: " + missingIds);
        }

        return studyPrograms;
    }

    public StudyProgramDTO convertToDto(StudyProgram studyProgram) {
        StudyProgramDTO dto = new StudyProgramDTO();
        dto.setId(studyProgram.getSpID());
        dto.setName(studyProgram.getName());
        return dto;
    }
}
