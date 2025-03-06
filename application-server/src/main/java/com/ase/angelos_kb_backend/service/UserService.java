package com.ase.angelos_kb_backend.service;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.ase.angelos_kb_backend.dto.UserDTO;
import com.ase.angelos_kb_backend.dto.UserDetailsDTO;
import com.ase.angelos_kb_backend.exception.ResourceNotFoundException;
import com.ase.angelos_kb_backend.exception.UnauthorizedException;
import com.ase.angelos_kb_backend.model.Organisation;
import com.ase.angelos_kb_backend.model.User;
import com.ase.angelos_kb_backend.repository.UserRepository;

import jakarta.mail.MessagingException;


@Service
public class UserService {

    private final UserRepository userRepository;
    private final OrganisationService organisationService;
    private final PasswordEncoder passwordEncoder;
    private final EmailService emailService;

    @Value("${cors.kb-ui}")
    private String kbOrigin;

    public UserService(UserRepository userRepository, OrganisationService organisationService, PasswordEncoder passwordEncoder, EmailService emailService) {
        this.userRepository = userRepository;
        this.organisationService = organisationService;
        this.passwordEncoder = passwordEncoder;
        this.emailService = emailService;
    }

    public List<UserDTO> getAllUsersByOrgId(Long orgId) {
        Organisation organisation = organisationService.getOrganisationById(orgId);
        if ("System Organisation".equals(organisation.getName())) {
            // Fetch all users if the organization is "System Organisation"
            return userRepository.findAll().stream().map(this::convertToDto).collect(Collectors.toList());
        }
        return userRepository.findByOrganisationOrgID(orgId).stream().map(this::convertToDto).collect(Collectors.toList());
    }

    public UserDTO findByMail(String mail) {
        return userRepository.findByMail(mail)
            .map(this::convertToDto) // Convert User to UserDTO if present
            .orElseThrow(() -> new ResourceNotFoundException("User not found with email: " + mail));
    }

    public UserDetailsDTO findMe(String mail) {
        User user = userRepository.findByMail(mail).orElseThrow(() -> new ResourceNotFoundException("User not found with email: " + mail));
        
        UserDetailsDTO userDetails = new UserDetailsDTO();
        userDetails.setId(user.getUserID());
        userDetails.setMail(user.getMail());
        userDetails.setAdmin(user.isAdmin());
        userDetails.setSystemAdmin(user.isSystemAdmin());
        userDetails.setApproved(user.isApproved());
        userDetails.setOrganisationName(user.getOrganisation().getName());
        userDetails.setOrganisationActive(Boolean.TRUE.equals(user.getOrganisation().getResponseActive()));
        
        return userDetails;
    }

    @Transactional
    public UserDTO approveUser(Long userId, Long orgId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id " + userId));
        Organisation approverOrg = organisationService.getOrganisationById(orgId);
        // Allow operation if the approver's organisation is "System Organisation" or matches the user's organisation
        if (!user.getOrganisation().getOrgID().equals(orgId) && !"System Organisation".equals(approverOrg.getName())) {
            throw new UnauthorizedException("You are not authorized to approve this user.");
        }
        user.setApproved(true);
        return convertToDto(userRepository.save(user));
    }

    // Set a user to admin
    @Transactional
    public UserDTO setUserToAdmin(Long userId, Long orgId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id " + userId));
        
        Organisation approverOrg = organisationService.getOrganisationById(orgId);
        // Allow operation if the approver's organisation is "System Organisation" or matches the user's organisation
        if (!user.getOrganisation().getOrgID().equals(orgId) && !"System Organisation".equals(approverOrg.getName())) {
            throw new UnauthorizedException("You are not authorized to make this user an administrator.");
        }

        user.setAdmin(true);
        User updatedUser = userRepository.save(user);
        return convertToDto(updatedUser);
    }

    @Transactional
    public UserDTO removeUser(Long userId, Long orgId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id " + userId));
        
        Organisation approverOrg = organisationService.getOrganisationById(orgId);
        // Allow operation if the approver's organisation is "System Organisation" or matches the user's organisation
        if (!user.getOrganisation().getOrgID().equals(orgId) && !"System Organisation".equals(approverOrg.getName())) {
            throw new UnauthorizedException("You are not authorized to make this user an administrator.");
        }

        user.setApproved(false);
        User updatedUser = userRepository.save(user);
        return convertToDto(updatedUser);
    }

    @Transactional
    public UserDTO registerUser(String email, String password, Long orgId) {
        // Check if the email is already in use
        if (userRepository.findByMail(email).isPresent() && userRepository.findByMail(email).get().isMailConfirmed()) {
            throw new ResourceNotFoundException("Email already in use");
        }
        Organisation organisation = organisationService.getOrganisationById(orgId);

        // Create and save the new user
        User newUser = new User();
        newUser.setMail(email);
        newUser.setPassword(passwordEncoder.encode(password));
        newUser.setOrganisation(organisation);
        newUser.setApproved(false); 
        newUser.setAdmin(false);
        newUser.setSystemAdmin(false);
        // Generate confirmation token
        String token = UUID.randomUUID().toString();
        newUser.setConfirmationToken(token);

        User savedUser = userRepository.save(newUser);

        // Send confirmation email
        try {
            sendConfirmationEmail(savedUser);
        } catch (MessagingException e) {
            throw new RuntimeException("Failed to send confirmation email. Registration aborted.", e);
        }

        return convertToDto(savedUser);
    }

    public boolean confirmUserEmail(String token) {
        User user = userRepository.findByConfirmationToken(token);
        if (user == null) {
            return false;
        }
        user.setMailConfirmed(true);
        user.setConfirmationToken(null); // Invalidate the token
        userRepository.save(user);
        return true;
    }

    private void sendConfirmationEmail(User user) throws MessagingException {
        String token = user.getConfirmationToken();

        String confirmationUrl = kbOrigin + "/knowledge-manager/confirm?token=" + token;
        String subject = "Email Confirmation";
    
        // Implement your email sending logic here
        emailService.sendEmail(user.getMail(), subject, confirmationUrl);
    }

    private UserDTO convertToDto(User user) {
        return UserDTO.builder()
            .id(user.getUserID())
            .mail(user.getMail())
            .isAdmin(user.isAdmin())
            .isApproved(user.isApproved())
            .build();
    }
}
