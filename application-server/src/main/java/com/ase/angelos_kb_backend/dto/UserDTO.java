package com.ase.angelos_kb_backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@ToString
public class UserDTO {
    private Long id;
    private String mail;
    @JsonProperty("isAdmin")
    private boolean isAdmin;
    @JsonProperty("isApproved")
    private boolean isApproved;
}
