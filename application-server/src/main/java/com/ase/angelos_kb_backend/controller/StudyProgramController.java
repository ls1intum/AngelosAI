package com.ase.angelos_kb_backend.controller;

import com.ase.angelos_kb_backend.dto.StudyProgramDTO;
import com.ase.angelos_kb_backend.service.StudyProgramService;
import com.ase.angelos_kb_backend.util.JwtUtil;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/study-programs")
public class StudyProgramController {

    private final StudyProgramService studyProgramService;
    private final JwtUtil jwtUtil;

    public StudyProgramController(StudyProgramService studyProgramService, JwtUtil jwtUtil) {
        this.studyProgramService = studyProgramService;
        this.jwtUtil = jwtUtil;
    }

    /**
     * Get all study programs by organisation ID extracted from JWT token.
     */
    @GetMapping
    public ResponseEntity<List<StudyProgramDTO>> getAllStudyPrograms(@RequestHeader("Authorization") String token) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        List<StudyProgramDTO> studyPrograms = studyProgramService.getAllStudyProgramsByOrgId(orgId);
        return ResponseEntity.ok(studyPrograms);
    }

    /**
     * Add an existing study program to an organisation.
     */
    @PostMapping("/{spId}/add-to-org")
    public ResponseEntity<Void> addStudyProgramToOrg(
            @RequestHeader("Authorization") String token,
            @PathVariable Long spId) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        studyProgramService.addStudyProgramToOrg(spId, orgId);
        return ResponseEntity.ok().build();
    }

    /**
     * Remove an existing study program from an organisation.
     */
    @DeleteMapping("/{spId}/remove-from-org")
    public ResponseEntity<Void> removeStudyProgramFromOrg(
            @RequestHeader("Authorization") String token,
            @PathVariable Long spId) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        studyProgramService.removeStudyProgramFromOrg(spId, orgId);
        return ResponseEntity.ok().build();
    }

    /**
     * Create a new study program for an organisation.
     */
    @PostMapping("/create")
    public ResponseEntity<StudyProgramDTO> createStudyProgram(
            @RequestHeader("Authorization") String token,
            @RequestParam String studyProgramName,
            @RequestParam(required = false) Long orgId) {
        Long callerOrgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));        
        boolean isSystemAdmin = jwtUtil.extractIsSystemAdmin(token.replace("Bearer ", ""));
        if (! (orgId != null && isSystemAdmin)) {
            orgId = callerOrgId;
        }
        StudyProgramDTO newStudyProgram = studyProgramService.createStudyProgram(studyProgramName, orgId);
        return ResponseEntity.ok(newStudyProgram);
    }

    /**
     * Delete a study program.
     */
    @DeleteMapping("/{spId}")
    public ResponseEntity<Void> deleteStudyProgram(
            @RequestHeader("Authorization") String token,
            @PathVariable Long spId) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        studyProgramService.deleteStudyProgram(spId, orgId);
        return ResponseEntity.ok().build();
    }
}
