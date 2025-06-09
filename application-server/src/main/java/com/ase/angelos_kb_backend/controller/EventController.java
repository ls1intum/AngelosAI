package com.ase.angelos_kb_backend.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.ase.angelos_kb_backend.dto.EventLogDTO;
import com.ase.angelos_kb_backend.dto.EventRequestDTO;
import com.ase.angelos_kb_backend.dto.LimitDTO;
import com.ase.angelos_kb_backend.dto.TimeframeRequestDTO;
import com.ase.angelos_kb_backend.model.EventLog;
import com.ase.angelos_kb_backend.service.AngelosService;
import com.ase.angelos_kb_backend.service.EunomiaService;
import com.ase.angelos_kb_backend.service.EventService;
import com.ase.angelos_kb_backend.util.JwtUtil;

@RestController
@RequestMapping("/api/event")
public class EventController {

    private final EventService eventService;
    private final EunomiaService eunomiaService;
    private final AngelosService angelosService;
    private final JwtUtil jwtUtil;

    @Value("${angelos.username}")
    private String angelosUsername;

    @Value("${angelos.password}")
    private String angelosPassword;

    @Value("${app.total.limit}")
    private int totalLimit;

    @Value("${app.chat.limit}")
    private int chatLimit;

    @Value("${app.mail.limit}")
    private int mailLimit;

    public EventController(EventService eventService, EunomiaService eunomiaService, AngelosService angelosService, JwtUtil jwtUtil) {
        this.eventService = eventService;
        this.eunomiaService = eunomiaService;
        this.angelosService = angelosService;
        this.jwtUtil = jwtUtil;
    }

    @PostMapping("/create")
    public ResponseEntity<EventLogDTO> createEvent(@RequestHeader("x-api-key") String apiKey,
        @RequestBody EventRequestDTO eventDto) {
        if (eunomiaService.verifyAPIKey(apiKey) || angelosService.verifyAPIKey(apiKey)) {
            if (eventDto.getEventType() == null || eventDto.getEventType().isBlank()) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
            }
            EventLog saved = eventService.logEvent(eventDto);
            EventLogDTO response = new EventLogDTO(saved.getId(), saved.getTimestamp(), saved.getEventType(), saved.getMetadata());
            return ResponseEntity.ok(response);
        } else {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
    }

    @PostMapping("/timeframe")
    public ResponseEntity<List<EventLogDTO>> getEventsInTimeframe(@RequestHeader("Authorization") String token,
        @RequestBody TimeframeRequestDTO requestDTO) {
        Long orgId = jwtUtil.extractOrgId(token.replace("Bearer ", ""));
        List<EventLogDTO> result = eventService.getEventsInTimeframe(requestDTO, orgId);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/limits")
    public ResponseEntity<LimitDTO> getLimits() {
        LimitDTO dto = new LimitDTO(totalLimit, chatLimit, mailLimit);
        return ResponseEntity.ok(dto);
    }
}
