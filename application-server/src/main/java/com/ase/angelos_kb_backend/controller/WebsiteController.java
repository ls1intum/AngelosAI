package com.ase.angelos_kb_backend.controller;

import com.ase.angelos_kb_backend.dto.WebsiteRequestDTO;
import com.ase.angelos_kb_backend.dto.WebsiteResponseDTO;
import com.ase.angelos_kb_backend.service.WebsiteService;
import com.ase.angelos_kb_backend.util.JwtUtil;

import jakarta.validation.Valid;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/websites")
public class WebsiteController {

    private final WebsiteService websiteService;
    private final JwtUtil jwtUtil;

    public WebsiteController(WebsiteService websiteService, JwtUtil jwtUtil) {
        this.websiteService = websiteService;
        this.jwtUtil = jwtUtil;
    }

    /**
     * Get all websites by organisation ID extracted from JWT token.
     */
    @GetMapping
    public ResponseEntity<List<WebsiteResponseDTO>> getAllWebsites(@RequestHeader("Authorization") String token) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        List<WebsiteResponseDTO> websites = websiteService.getAllWebsitesByOrgId(orgId);
        return ResponseEntity.ok(websites);
    }

    /**
     * Add a new website.
     * - Add request to Angelos.
     * - Computes content hash.
     * - If content has changed, sends update request and sets updated flag.
     */
    @PostMapping
    public ResponseEntity<WebsiteResponseDTO> addWebsite(
            @RequestHeader("Authorization") String token,
            @Valid @RequestBody WebsiteRequestDTO websiteRequestDTO) {

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        WebsiteResponseDTO responseDTO = websiteService.addWebsite(orgId, websiteRequestDTO);
        return ResponseEntity.ok(responseDTO);
    }

    /**
     * Edit an existing website by ID.
     * - If the link has changed, calls Angelos parser, computes content hash.
     * - If content has changed, sends update request and updates content hash.
     * - If only the title changed, just updates the database.
     */
    @PutMapping("/{websiteId}")
    public ResponseEntity<WebsiteResponseDTO> editWebsite(
            @RequestHeader("Authorization") String token,
            @PathVariable UUID websiteId,
            @Valid @RequestBody WebsiteRequestDTO websiteRequestDTO) {

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));

        WebsiteResponseDTO responseDTO = websiteService.editWebsite(orgId, websiteId, websiteRequestDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * Delete a website by ID.
     * - Sends delete request to Angelos.
     * - If successful, deletes the website from the database.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteWebsite(
            @RequestHeader("Authorization") String token,
            @PathVariable UUID id) {

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        websiteService.deleteWebsite(id, orgId);
        return ResponseEntity.ok().build();
    }
}