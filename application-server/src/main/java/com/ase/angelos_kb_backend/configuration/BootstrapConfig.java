package com.ase.angelos_kb_backend.configuration;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import com.ase.angelos_kb_backend.model.Organisation;
import com.ase.angelos_kb_backend.model.User;
import com.ase.angelos_kb_backend.repository.OrganisationRepository;
import com.ase.angelos_kb_backend.repository.UserRepository;

@Component
public class BootstrapConfig {

    private final UserRepository userRepository;
    private final OrganisationRepository organisationRepository;
    private final PasswordEncoder passwordEncoder;

    @Value("${admin.default.email}")
    private String defaultAdminEmail;

    @Value("${admin.default.password}")
    private String defaultAdminPassword;

    public BootstrapConfig(UserRepository userRepository, 
                           OrganisationRepository organisationRepository,
                           PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.organisationRepository = organisationRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void createDefaultAdmin() {
        // Ensure the "System Organisation" exists
        Organisation systemOrg = organisationRepository.findByName("System Organisation")
            .orElseGet(() -> {
                Organisation org = new Organisation();
                org.setName("System Organisation");
                return organisationRepository.save(org);
            });

        // Check if the default admin user exists
        if (!userRepository.existsByMail(defaultAdminEmail)) {
            User admin = new User();
            admin.setMail(defaultAdminEmail);
            admin.setPassword(passwordEncoder.encode(defaultAdminPassword)); // Use encoded password
            admin.setAdmin(true);
            admin.setApproved(true);
            admin.setSystemAdmin(true);
            admin.setMailConfirmed(true);
            admin.setOrganisation(systemOrg); // Assign the "System Organisation"
            userRepository.save(admin);
        }
    }
}