package com.ase.angelos_kb_backend.repository;

import com.ase.angelos_kb_backend.model.StudyProgram;
import com.ase.angelos_kb_backend.model.WebsiteContent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface WebsiteContentRepository extends JpaRepository<WebsiteContent, UUID> {
    List<WebsiteContent> findByOrganisationOrgID(Long orgId);
    Optional<WebsiteContent> findByLink(String link);

    @Query("SELECT w FROM WebsiteContent w WHERE SIZE(w.studyPrograms) = 1 AND :studyProgram MEMBER OF w.studyPrograms")
    List<WebsiteContent> findByStudyProgramsContainsOnly(@Param("studyProgram") StudyProgram studyProgram);

    @Query("SELECT w FROM WebsiteContent w WHERE :sp MEMBER OF w.studyPrograms")
    List<WebsiteContent> findByStudyProgramsContains(@Param("sp") StudyProgram sp);
}