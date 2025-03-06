package com.ase.angelos_kb_backend.model;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

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
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import lombok.ToString;

@Entity
@Data
public class DocumentContent {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID docID;

    private String title;

    private String filename;

    @NotNull
    private String originalFilename;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @ManyToOne
    @JoinColumn(name = "org_id", nullable = false)
    @ToString.Exclude
    private Organisation organisation;

    @ManyToMany
    @JoinTable(
        name = "DocumentStudyPrograms",
        joinColumns = @JoinColumn(name = "doc_id"),
        inverseJoinColumns = @JoinColumn(name = "sp_id")
    )
    private List<StudyProgram> studyPrograms;

    private String contentHash;

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
