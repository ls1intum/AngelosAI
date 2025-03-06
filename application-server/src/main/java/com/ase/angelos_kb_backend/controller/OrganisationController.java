package com.ase.angelos_kb_backend.controller;

import com.ase.angelos_kb_backend.dto.OrganisationDTO;
import com.ase.angelos_kb_backend.service.OrganisationService;
import com.ase.angelos_kb_backend.util.JwtUtil;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/organisations")
public class OrganisationController {

    private final OrganisationService organisationService;
    private final JwtUtil jwtUtil;

    public OrganisationController(OrganisationService organisationService, JwtUtil jwtUtil) {
        this.organisationService = organisationService;
        this.jwtUtil = jwtUtil;
    }

    /**
     * Get all organisations.
     * This endpoint is unprotected and returns all organisations except the System Organisation as a list of OrganisationDTOs.
     */
    @GetMapping
    public ResponseEntity<List<OrganisationDTO>> getAllOrganisations() {
        List<OrganisationDTO> organisations = organisationService.getAllOrganisations()
            .stream()
            .filter(org -> !"System Organisation".equals(org.getName()))
            .collect(Collectors.toList());
        return ResponseEntity.ok(organisations);
    }

    /**
     * Add a new organisation. Only accessible by system admin.
     */
    @PostMapping
    public ResponseEntity<OrganisationDTO> addOrganisation(
            @RequestHeader("Authorization") String token,
            @RequestParam String name) {
        // Verify system admin access
        if (!jwtUtil.extractIsSystemAdmin(token.replace("Bearer ", ""))) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }

        OrganisationDTO newOrganisation = organisationService.addOrganisation(name);
        return ResponseEntity.status(HttpStatus.CREATED).body(newOrganisation);
    }

    /**
     * Update an existing organisation. Only accessible by system admin.
     */
    @PutMapping("/{id}")
    public ResponseEntity<OrganisationDTO> updateOrganisation(
            @RequestHeader("Authorization") String token,
            @PathVariable Long id,
            @RequestBody OrganisationDTO organisation) {
        if (!jwtUtil.extractIsSystemAdmin(token.replace("Bearer ", ""))) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        OrganisationDTO newOrganisation = organisationService.updateOrganisation(id, organisation);
        if (newOrganisation == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
        return ResponseEntity.ok(newOrganisation);
    }

    /**
     * Remove an organisation by ID. Only accessible by system admin.
     */
    @DeleteMapping("/{orgId}")
    public ResponseEntity<String> removeOrganisation(
            @RequestHeader("Authorization") String token,
            @PathVariable Long orgId) {
        // Verify system admin access
        if (!jwtUtil.extractIsSystemAdmin(token.replace("Bearer ", ""))) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("Access denied.");
        }

        boolean isRemoved = organisationService.removeOrganisation(orgId);
        if (isRemoved) {
            return ResponseEntity.ok("Organisation removed successfully.");
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Organisation not found.");
        }
    }

    @PutMapping("/chatActive")
    public ResponseEntity<OrganisationDTO> setChatStatus(
            @RequestHeader("Authorization") String token,
            @RequestParam boolean active) {

        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        OrganisationDTO updatedOrg = organisationService.setResponseActive(orgId, active);

        if (updatedOrg == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
        return ResponseEntity.ok(updatedOrg);
    }

    @PutMapping("/mailActive")
    public ResponseEntity<OrganisationDTO> setMailStatus(
            @RequestHeader("Authorization") String token,
            @RequestParam boolean active) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        boolean success = organisationService.setMailActive(orgId, active);

        if (! success) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
        return ResponseEntity.ok().build();
    }
}
