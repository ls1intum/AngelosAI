package com.ase.angelos_kb_backend.repository;

import com.ase.angelos_kb_backend.model.DocumentContent;
import com.ase.angelos_kb_backend.model.StudyProgram;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.UUID;

public interface DocumentContentRepository extends JpaRepository<DocumentContent, UUID> {
    List<DocumentContent> findByOrganisationOrgID(Long orgId);

    @Query("SELECT d FROM DocumentContent d WHERE SIZE(d.studyPrograms) = 1 AND :studyProgram MEMBER OF d.studyPrograms")
    List<DocumentContent> findByStudyProgramsContainsOnly(@Param("studyProgram") StudyProgram studyProgram);

    @Query("SELECT d FROM DocumentContent d WHERE :sp MEMBER OF d.studyPrograms")
    List<DocumentContent> findByStudyProgramsContains(@Param("sp") StudyProgram sp);
}