package com.ase.angelos_kb_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Data;


@Data
@AllArgsConstructor
public class LimitDTO {
    private int totalLimit;
    private int chatLimit;
    private int mailLimit;
}
