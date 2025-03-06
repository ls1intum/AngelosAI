package com.ase.angelos_kb_backend.repository;

import com.ase.angelos_kb_backend.model.SampleQuestion;
import com.ase.angelos_kb_backend.model.StudyProgram;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.UUID;

public interface SampleQuestionRepository extends JpaRepository<SampleQuestion, UUID> {
    List<SampleQuestion> findByOrganisationOrgID(Long orgId);

    @Query("SELECT s FROM SampleQuestion s WHERE SIZE(s.studyPrograms) = 1 AND :studyProgram MEMBER OF s.studyPrograms")
    List<SampleQuestion> findByStudyProgramsContainsOnly(@Param("studyProgram") StudyProgram studyProgram);

    @Query("SELECT s FROM SampleQuestion s WHERE :sp MEMBER OF s.studyPrograms")
    List<SampleQuestion> findByStudyProgramsContains(@Param("sp") StudyProgram sp);
}
