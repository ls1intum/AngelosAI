package com.ase.angelos_kb_backend.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import com.ase.angelos_kb_backend.dto.EventLogDTO;
import com.ase.angelos_kb_backend.dto.EventRequestDTO;
import com.ase.angelos_kb_backend.dto.TimeframeRequestDTO;
import com.ase.angelos_kb_backend.model.EventLog;
import com.ase.angelos_kb_backend.model.Organisation;
import com.ase.angelos_kb_backend.repository.EventRepository;

@Service
public class EventService {
    private final EventRepository eventLogRepository;
    private final OrganisationService organisationService;

    public EventService(EventRepository eventLogRepository, OrganisationService organisationService) {
        this.eventLogRepository = eventLogRepository;
        this.organisationService = organisationService;
    }

    public EventLog logEvent(EventRequestDTO dto) {
        Organisation organisation = organisationService.getOrganisationById(dto.getOrgID());

        EventLog event = new EventLog();
        event.setEventType(dto.getEventType());
        event.setMetadata(dto.getMetadata());
        event.setOrganisation(organisation);
        return eventLogRepository.save(event);
    }

    public List<EventLogDTO> getEventsInTimeframe(TimeframeRequestDTO timeframe, Long orgID) {
        List<EventLog> events = eventLogRepository.findByOrganisationOrgIDAndTimestampBetween(
            orgID, timeframe.getFrom(), timeframe.getTo()
        );
    
        return events.stream()
            .map(event -> {
                EventLogDTO dto = new EventLogDTO(event.getId(), event.getTimestamp(), event.getEventType(), event.getMetadata());
                return dto;
            })
            .collect(Collectors.toList());
    }

    @Async
    public void logEventAsync(String eventType, String metadata, Long orgID) {
        Organisation organisation = organisationService.getOrganisationById(orgID);

        EventLog event = new EventLog();
        event.setEventType(eventType);
        event.setMetadata(metadata);
        event.setOrganisation(organisation);
        eventLogRepository.save(event);
    }
}
