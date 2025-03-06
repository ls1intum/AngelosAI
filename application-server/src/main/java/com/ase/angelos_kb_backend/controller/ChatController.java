package com.ase.angelos_kb_backend.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import com.ase.angelos_kb_backend.dto.LoginRequestDTO;
import com.ase.angelos_kb_backend.dto.StudyProgramDTO;
import com.ase.angelos_kb_backend.dto.angelos.AngelosChatMessage;
import com.ase.angelos_kb_backend.dto.angelos.AngelosChatRequest;
import com.ase.angelos_kb_backend.dto.angelos.AngelosChatResponse;
import com.ase.angelos_kb_backend.service.AngelosService;
import com.ase.angelos_kb_backend.service.OrganisationService;
import com.ase.angelos_kb_backend.service.StudyProgramService;
import com.ase.angelos_kb_backend.util.JwtUtil;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;



@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final JwtUtil jwtUtil;
    private final AngelosService angelosService;
    private final StudyProgramService studyProgramService;
    private final OrganisationService organisationService;

    @Value("${angelos.username}")
    private String angelosUsername;

    @Value("${angelos.password}")
    private String angelosPassword;

    @Value("${app.max-message-length}")
    private int maxMessageLength;

    public ChatController(JwtUtil jwtUtil, AngelosService angelosService, StudyProgramService studyProgramService, OrganisationService organisationService) {
        this.jwtUtil = jwtUtil;
        this.angelosService = angelosService;
        this.studyProgramService = studyProgramService;
        this.organisationService = organisationService;
    }

    /**
     * Route chat requests
     * TODO: Add rate limiting, storing session history...
     */
    @PostMapping("/send")
    public ResponseEntity<AngelosChatResponse> chat(@RequestHeader("ChatAuth") String token, 
            @RequestBody AngelosChatRequest request,
            @RequestParam(defaultValue = "false") boolean filterByOrg) {
        token = token.replace("Bearer ", "");
        if (jwtUtil.extractEmail(token).equals(angelosUsername) && jwtUtil.extractChatPassword(token).equals(angelosPassword)) {
            Long orgId = request.getOrgId();
            if (orgId != null && ! this.organisationService.isResponseActive(orgId)) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
            }
            
            // Validate messages and last message length
            if (request.getMessages() == null || request.getMessages().isEmpty()) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "No messages have been provided.");
            }

            AngelosChatMessage lastMessage = request.getMessages().get(request.getMessages().size() - 1);
            if (lastMessage != null && lastMessage.getMessage().length() > maxMessageLength) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, 
                        "Message length exceeds the allowed limit of " + maxMessageLength + " characters.");
            }
            
            return ResponseEntity.ok(this.angelosService.sendChatMessage(request, filterByOrg));
        } else {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
    }

    /**
     * Preliminary login.
     * TODO: Remove
     */
    @PostMapping("/login")
    public ResponseEntity<Map<String, String>> postMethodName(@RequestHeader("x-api-key") String apiKey, @RequestBody LoginRequestDTO body) {

        System.out.println(body);
        if (angelosService.verifyAPIKey(apiKey) && body.getEmail().equals(angelosUsername) && body.getPassword().equals(angelosPassword)) {
            String chatToken = jwtUtil.generateChatToken(body.getEmail(), body.getPassword());
            return ResponseEntity.ok().body(Map.of("accessToken", chatToken));
        } else {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
    }

    @GetMapping("/study-programs/{orgId}")
    public ResponseEntity<List<StudyProgramDTO>> getMethodName(@RequestHeader("ChatAuth") String token, 
            @PathVariable Long orgId, 
            @RequestParam(defaultValue = "false") boolean filterByOrg) {
        token = token.replace("Bearer ", "");
        List<StudyProgramDTO> studyPrograms = new ArrayList<>();
        if (jwtUtil.extractEmail(token).equals(angelosUsername) && jwtUtil.extractChatPassword(token).equals(angelosPassword)) {
            if (filterByOrg) {
                studyPrograms = studyProgramService.getAllStudyProgramsByOrgId(orgId);
            } else {
                studyPrograms = studyProgramService.getAllStudyPrograms();
            }
            return ResponseEntity.ok(studyPrograms);
        } else {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
    }
    
}
