package com.ase.angelos_kb_backend.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import com.ase.angelos_kb_backend.dto.angelos.AngelosChatResponse;
import com.ase.angelos_kb_backend.dto.eunomia.MailCredentialsDTO;
import com.ase.angelos_kb_backend.dto.eunomia.MailCredentialsResponseDTO;
import com.ase.angelos_kb_backend.dto.eunomia.MailResponseRequestDTO;
import com.ase.angelos_kb_backend.dto.eunomia.MailStatusDTO;
import com.ase.angelos_kb_backend.dto.eunomia.MailThreadRequestDTO;
import com.ase.angelos_kb_backend.service.AngelosService;
import com.ase.angelos_kb_backend.service.EunomiaService;
import com.ase.angelos_kb_backend.service.OrganisationService;
import com.ase.angelos_kb_backend.service.StudyProgramService;
import com.ase.angelos_kb_backend.util.JwtUtil;
import com.ase.angelos_kb_backend.util.MailStatus;


@RestController
@RequestMapping("/api/mail")
public class MailController {

    private final OrganisationService organisationService;
    private final StudyProgramService studyProgramService;
    private final JwtUtil jwtUtil;
    private final EunomiaService eunomiaService;
    private final AngelosService angelosService;

    @Value("${app.max-message-length}")
    private int maxMessageLength;

    public MailController(OrganisationService organisationService, StudyProgramService studyProgramService, JwtUtil jwtUtil, EunomiaService eunomiaService, AngelosService angelosService) {
        this.jwtUtil = jwtUtil;
        this.organisationService = organisationService;
        this.studyProgramService = studyProgramService;
        this.eunomiaService = eunomiaService;
        this.angelosService = angelosService;
    }


    /**
     * Set (or update) mail credentials for a specific organisation.
     * Called by the Knowledge Base UI to activate/configure the mail pipeline.
     */
    @PostMapping(path="/set-credentials", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Void> setCredentials(
            @RequestHeader("Authorization") String token,
            @RequestBody MailCredentialsDTO credentialsDto) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        boolean success = false;

        if (credentialsDto.getMailAccount() != null && credentialsDto.getMailPassword()!= null) {
            organisationService.setCredentials(orgId, credentialsDto);

            MailThreadRequestDTO dto = new MailThreadRequestDTO();
            dto.setMailAccount(credentialsDto.getMailAccount());
            dto.setMailPassword(credentialsDto.getMailPassword());

            List<String> studyPrograms = studyProgramService.getAllStudyProgramsByOrgId(orgId).stream().map(sp -> sp.getName()).toList();
            dto.setStudyPrograms(studyPrograms);

            success = eunomiaService.startThread(orgId, dto);
        }

        if (success) {
            organisationService.setMailStatus(orgId, MailStatus.ACTIVE);
            return ResponseEntity.ok().build();
        } else {
            organisationService.setMailStatus(orgId, MailStatus.INACTIVE);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build(); 
        }
    }

    /**
     * Get mail credentials for a specific organisation.
     * Called by the Knowledge Base UI to show the currently configured mail address.
     */
    @GetMapping("/credentials")
    public ResponseEntity<MailCredentialsResponseDTO> getCredentials(
            @RequestHeader("Authorization") String token) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        MailCredentialsResponseDTO response = new MailCredentialsResponseDTO();
        response.setMailAccount(organisationService.getCredentials(orgId));
        return ResponseEntity.ok(response);
    }

    /**
     * Deactivate the mail pipeline for this organisation.
     * To be called by the UI to deactivate the pipeline
     */
    @PostMapping("/deactivate")
    public ResponseEntity<Void> deactivate(@RequestHeader("Authorization") String token) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        boolean success = eunomiaService.stopThread(orgId);
        if (success) {
            organisationService.setMailStatus(orgId, MailStatus.INACTIVE);
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build(); 
        }
    }

    /**
     * Get the current mail pipeline status (ACTIVE, INACTIVE, ERROR, etc.)
     * To be called by UI to indicate status in UI
     */
    @GetMapping("/status")
    public ResponseEntity<MailStatusDTO> getStatus(@RequestHeader("Authorization") String token) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));

        MailStatusDTO statusDto = new MailStatusDTO();
        MailStatus status = eunomiaService.getStatus(orgId).getStatus();

        statusDto.setStatus(status);
        organisationService.setMailStatus(orgId, status);

        return ResponseEntity.ok(statusDto);
    }

    /**
     * Forwards "ask" requests from the mail pipeline to the Angelos RAG, 
     */
    @PostMapping("/ask")
    public ResponseEntity<AngelosChatResponse> ask(
            @RequestHeader("x-api-key") String apiKey,
            @RequestBody MailResponseRequestDTO request) {

        if (eunomiaService.verifyAPIKey(apiKey)) {
            if (request.getMessage() != null && request.getMessage().length() > maxMessageLength) {
                throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "Message length exceeds the allowed limit of " + maxMessageLength + " characters."
                );
            }
            // Forward to Angelos
            AngelosChatResponse ragResponse = angelosService.sendAskRequest(request);
            return ResponseEntity.ok(ragResponse);
        } else {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
    }

}
