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
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Entity
@Data
public class WebsiteContent {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @NotBlank(message = "Link must not be blank")
    private String link;

    @NotBlank(message = "Title must not be blank")
    private String title;

    private String contentHash;

    @ManyToOne
    @JoinColumn(name = "org_id", nullable = false)
    private Organisation organisation;

    @ManyToMany
    @JoinTable(
        name = "WebsiteStudyPrograms",
        joinColumns = @JoinColumn(name = "web_id"),
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
