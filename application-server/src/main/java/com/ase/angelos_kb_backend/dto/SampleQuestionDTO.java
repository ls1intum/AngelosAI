package com.ase.angelos_kb_backend.dto;

import java.util.List;

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
public class SampleQuestionDTO {
    private String id;
    private String topic;
    private String question;
    private String answer;
    private List<StudyProgramDTO> studyPrograms;
}
