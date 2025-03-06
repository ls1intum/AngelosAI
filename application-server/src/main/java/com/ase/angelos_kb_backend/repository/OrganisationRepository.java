package com.ase.angelos_kb_backend.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.ase.angelos_kb_backend.model.Organisation;


public interface OrganisationRepository extends JpaRepository<Organisation, Long> {
    Optional<Organisation> findByName(String name);
}
