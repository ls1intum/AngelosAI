package com.ase.angelos_kb_backend.dto.eunomia;

import com.ase.angelos_kb_backend.util.MailStatus;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MailStatusDTO {
    MailStatus status;
}
