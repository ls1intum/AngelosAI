package com.ase.angelos_kb_backend.model;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.JoinTable;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import lombok.Data;
import lombok.ToString;

@Entity
@Data
public class SampleQuestion {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID sqID;

    private String topic;

    @Column(length = 1000)
    private String question;

    @Column(length = 1000)
    private String answer;

    @ManyToOne
    @JoinColumn(name = "org_id", nullable = false)
    @ToString.Exclude
    private Organisation organisation;

    @ManyToMany
    @JoinTable(
        name = "SampleQuestionStudyPrograms",
        joinColumns = @JoinColumn(name = "sq_id"),
        inverseJoinColumns = @JoinColumn(name = "sp_id")
    )
    private List<StudyProgram> studyPrograms;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        LocalDateTime now = LocalDateTime.now();
        createdAt = now;
        updatedAt = now;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
