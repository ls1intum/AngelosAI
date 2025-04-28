package com.ase.angelos_kb_backend.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
@JsonInclude(Include.NON_NULL)
public class UserDetailsDTO extends UserDTO {
    private String organisationName;
    @JsonProperty("isSystemAdmin")
    private boolean isSystemAdmin;
    private boolean organisationActive;
    private String organisationUrl;
}