package com.ase.angelos_kb_backend.repository;

import com.ase.angelos_kb_backend.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByOrganisationOrgID(Long orgId);
    Optional<User> findByMail(String mail);
    User findByConfirmationToken(String token);
    boolean existsByMail(String mail);
}
