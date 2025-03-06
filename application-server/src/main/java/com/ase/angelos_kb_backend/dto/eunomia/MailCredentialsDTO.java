package com.ase.angelos_kb_backend.dto.eunomia;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MailCredentialsDTO {
    @JsonProperty("mailAccount")
    private String mailAccount;
    @JsonProperty("mailPassword")
    private String mailPassword;
}
