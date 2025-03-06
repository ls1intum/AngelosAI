package com.ase.angelos_kb_backend.dto.eunomia;

import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MailThreadRequestDTO {
    private String mailAccount;
    private String mailPassword;
    private List<String> studyPrograms;
}
