package com.ase.angelos_kb_backend.controller;

import java.util.List;
import java.util.UUID;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.ase.angelos_kb_backend.dto.SampleQuestionDTO;
import com.ase.angelos_kb_backend.service.SampleQuestionService;
import com.ase.angelos_kb_backend.util.JwtUtil;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/sample-questions")
public class SampleQuestionController {

    private final SampleQuestionService sampleQuestionService;
    private final JwtUtil jwtUtil;

    public SampleQuestionController(SampleQuestionService sampleQuestionService, JwtUtil jwtUtil) {
        this.sampleQuestionService = sampleQuestionService;
        this.jwtUtil = jwtUtil;
    }

    /**
     * Get all sample questions by organisation ID extracted from JWT token.
     */
    @GetMapping
    public ResponseEntity<List<SampleQuestionDTO>> getAllSampleQuestions(@RequestHeader("Authorization") String token) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        List<SampleQuestionDTO> sampleQuestions = sampleQuestionService.getAllSampleQuestionsByOrgId(orgId);
        return ResponseEntity.ok(sampleQuestions);
    }

    /**
     * Add a new sample question.
     */
    @PostMapping
    public ResponseEntity<SampleQuestionDTO> addSampleQuestion(
            @RequestHeader("Authorization") String token,
            @Valid @RequestBody SampleQuestionDTO sampleQuestionDTO) {
        try {
            Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
            SampleQuestionDTO responseDTO = sampleQuestionService.addSampleQuestion(orgId, sampleQuestionDTO);
            return ResponseEntity.ok(responseDTO);
        } catch (Exception e) {
            System.err.println("Error adding sample question: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(null); // Adjust response as necessary for your API's design
        }
    }

    /**
     * Edit an existing sample question by ID.
     */
    @PutMapping("/{sampleQuestionId}")
    public ResponseEntity<SampleQuestionDTO> editSampleQuestion(
            @RequestHeader("Authorization") String token,
            @PathVariable UUID sampleQuestionId,
            @Valid @RequestBody SampleQuestionDTO sampleQuestionDTO) {

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        SampleQuestionDTO responseDTO = sampleQuestionService.editSampleQuestion(orgId, sampleQuestionId, sampleQuestionDTO);
        return ResponseEntity.ok(responseDTO);
    }

    /**
     * Delete a sample question by ID.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteSampleQuestion(
            @RequestHeader("Authorization") String token,
            @PathVariable UUID id) {

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        sampleQuestionService.deleteSampleQuestion(id, orgId);
        return ResponseEntity.ok().build();
    }
}
