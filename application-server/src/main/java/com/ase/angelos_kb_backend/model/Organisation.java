package com.ase.angelos_kb_backend.model;

import java.util.List;

import com.ase.angelos_kb_backend.util.MailStatus;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.Data;

@Entity
@Data
@Table(name = "organisations", uniqueConstraints = @UniqueConstraint(columnNames = "name"))
public class Organisation {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long orgID;

    private String name;

    private String mailAccount;
    private MailStatus mailStatus;

    @Column(nullable = true)
    private Boolean responseActive = true;

    @OneToMany(mappedBy = "organisation", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<User> users;

    @OneToMany(mappedBy = "organisation", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<StudyProgram> studyPrograms;

    @OneToMany(mappedBy = "organisation", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<WebsiteContent> websites;

    @OneToMany(mappedBy = "organisation", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<DocumentContent> documents;

    @OneToMany(mappedBy = "organisation", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<SampleQuestion> sampleQuestions;
}
