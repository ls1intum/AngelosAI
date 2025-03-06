package com.ase.angelos_kb_backend.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.ToString;

@Entity
@Table(name = "users")
@Data
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long userID;

    private String mail;

    private String password;

    private boolean isAdmin;

    private boolean isApproved;

    private boolean mailConfirmed;
    private String confirmationToken;

    private boolean isSystemAdmin;

    @ManyToOne
    @JoinColumn(name = "org_id", nullable = false)
    @ToString.Exclude
    private Organisation organisation;
}
