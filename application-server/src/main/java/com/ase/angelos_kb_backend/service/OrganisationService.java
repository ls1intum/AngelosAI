package com.ase.angelos_kb_backend.service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import com.ase.angelos_kb_backend.dto.OrganisationDTO;
import com.ase.angelos_kb_backend.dto.eunomia.MailCredentialsDTO;
import com.ase.angelos_kb_backend.exception.ResourceNotFoundException;
import com.ase.angelos_kb_backend.model.Organisation;
import com.ase.angelos_kb_backend.repository.OrganisationRepository;
import com.ase.angelos_kb_backend.util.MailStatus;

@Service
public class OrganisationService {

    private final OrganisationRepository organisationRepository;
    private final EunomiaService eunomiaService;

    public OrganisationService(OrganisationRepository organisationRepository, EunomiaService eunomiaService) {
        this.organisationRepository = organisationRepository;
        this.eunomiaService = eunomiaService;
    }

    public Organisation getOrganisationById(Long id) {
        return organisationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Organisation not found with ID: " + id));
    }

    public OrganisationDTO addOrganisation(String name) {
        Organisation organisation = new Organisation();
        organisation.setName(name);

        Organisation savedOrganisation = organisationRepository.save(organisation);
        return convertToDto(savedOrganisation);
    }

    public OrganisationDTO updateOrganisation(Long id, OrganisationDTO updatedOrganisation) {
        Optional<Organisation> optionalOrg = organisationRepository.findById(id);
        if(optionalOrg.isEmpty()) {
            return null;
        }
        Organisation existingOrg = optionalOrg.get();
        if (updatedOrganisation.getName() != null) {
            existingOrg.setName(updatedOrganisation.getName());
        }
        Organisation savedOrg = organisationRepository.save(existingOrg);
        return convertToDto(savedOrg);
    }

    public boolean removeOrganisation(Long orgId) {
        if (organisationRepository.existsById(orgId)) {
            organisationRepository.deleteById(orgId);
            return true;
        } else {
            throw new ResourceNotFoundException("Organisation not found with id " + orgId);
        }
    }

    public List<OrganisationDTO> getAllOrganisations() {
        List<Organisation> organisations = organisationRepository.findAll();
        return organisations.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    public void setCredentials(Long orgId, MailCredentialsDTO credentialsDTO) {
        Organisation org = this.getOrganisationById(orgId);
        
        org.setMailAccount(credentialsDTO.getMailAccount());
        org.setMailStatus(MailStatus.INACTIVE);

        organisationRepository.save(org);
    }

    public String getCredentials(Long orgId) {
        Organisation org = this.getOrganisationById(orgId);
        return org.getMailAccount();
    }

    public void setMailStatus(Long orgId, MailStatus status) {
        Organisation org = this.getOrganisationById(orgId);
        org.setMailStatus(status);

        organisationRepository.save(org);
    }

    public List<OrganisationDTO> getOrganisationsForMail() {
        List<OrganisationDTO> result = organisationRepository.findAll().stream()
            .filter(a -> !a.getMailAccount().equals(null))
            .map(this::convertToDto)
            .collect(Collectors.toList());
        return result;
    }

    public boolean setMailActive(Long orgId, boolean active) {
        // TODO: Pause Eunomia and reactivate
        Optional<Organisation> optionalOrg = organisationRepository.findById(orgId);
        if (optionalOrg.isEmpty()) {
            throw new RuntimeException();
        }
        boolean success = this.eunomiaService.stopThread(orgId);
        if (success) {
            return true;
        } else {
            throw new RuntimeException();
        }
    }

    @Cacheable("orgResponseActive") // or your chosen cache name
    public boolean isResponseActive(Long orgId) {
        return organisationRepository.findById(orgId)
                .map(Organisation::getResponseActive)
                .orElse(false);
    }

    @CacheEvict(value = "orgResponseActive", key = "#orgId")
    public OrganisationDTO setResponseActive(Long orgId, boolean active) {
        Optional<Organisation> optionalOrg = organisationRepository.findById(orgId);
        if (optionalOrg.isEmpty()) {
            return null;
        }

        Organisation org = optionalOrg.get();
        org.setResponseActive(active);
    
        Organisation saved = organisationRepository.save(org);
        return convertToDto(saved);
    }

    private OrganisationDTO convertToDto(Organisation organisation) {
        OrganisationDTO dto = new OrganisationDTO();
        dto.setId(organisation.getOrgID());
        dto.setName(organisation.getName());
        return dto;
    }
}
