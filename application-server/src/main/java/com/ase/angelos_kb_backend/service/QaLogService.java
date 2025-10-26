package com.ase.angelos_kb_backend.service;

import com.ase.angelos_kb_backend.dto.QaLogDTO;
import com.ase.angelos_kb_backend.model.QaLog;
import com.ase.angelos_kb_backend.repository.QaLogRepository;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class QaLogService {

    private final QaLogRepository qaLogRepository;

    public QaLogService(QaLogRepository repo) {
        this.qaLogRepository = repo;
    }

    @Transactional
    public void log(String question, String answer, String studyProgram, Long orgId) {
        QaLog log = new QaLog();
        log.setQuestion(question);
        log.setAnswer(answer);
        log.setStudyProgram(studyProgram);
        log.setOrgId(orgId);
        qaLogRepository.save(log);
    }

    @Async
    public void logAsync(String question, String answer, String studyProgram, Long orgId) {
        try {
            QaLog log = new QaLog();
            log.setQuestion(question);
            log.setAnswer(answer);
            log.setStudyProgram(studyProgram);
            log.setOrgId(orgId);
            qaLogRepository.save(log);
        } catch (Exception e) {
            System.err.println("QA log failed: " + e.getMessage());
        }
    }

    public List<QaLogDTO> getAll() {
        return qaLogRepository.findAllByOrderByCreatedAtDesc()
                   .stream().map(this::toDto).collect(Collectors.toList());
    }

    public List<QaLogDTO> getByOrg(Long orgId) {
        return qaLogRepository.findByOrgIdOrderByCreatedAtDesc(orgId)
                   .stream().map(this::toDto).collect(Collectors.toList());
    }

    private QaLogDTO toDto(QaLog q) {
        return new QaLogDTO(
            q.getId().toString(), 
            q.getCreatedAt(), 
            q.getQuestion(), 
            q.getAnswer(), 
            q.getStudyProgram(), 
            q.getOrgId()
        );
    }
}