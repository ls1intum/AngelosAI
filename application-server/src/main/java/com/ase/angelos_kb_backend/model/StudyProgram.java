package com.ase.angelos_kb_backend.model;


import java.util.List;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.ManyToOne;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Entity
@Data
public class StudyProgram {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long spID;

    @NotBlank(message = "Name cannot be empty or blank")
    @Column(nullable = false)
    private String name;

    @ManyToOne
    private Organisation organisation;

    @ManyToMany(mappedBy = "studyPrograms")
    private List<WebsiteContent> websites;

    @ManyToMany(mappedBy = "studyPrograms")
    private List<DocumentContent> documents;
}
