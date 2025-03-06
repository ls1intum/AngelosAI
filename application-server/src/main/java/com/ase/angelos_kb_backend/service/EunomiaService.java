package com.ase.angelos_kb_backend.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import com.ase.angelos_kb_backend.dto.eunomia.MailStatusDTO;
import com.ase.angelos_kb_backend.dto.eunomia.MailThreadRequestDTO;
import com.ase.angelos_kb_backend.util.MailStatus;

@Component
public class EunomiaService {
    
    @Value("${eunomia.url}")
    private String eunomiaUrl;

    @Value("${eunomia.secret}")
    private String eunomiaApiKey;

    private final RestTemplate restTemplate;

    public EunomiaService() {
        this.restTemplate = new RestTemplate();
    }

    /**
     * Check the status of the mail pipeline for a specific organization.
     *
     * @param orgId The organization ID
     * @return MailStatusDTO with the pipeline's status
     */
    public MailStatusDTO getStatus(Long orgId) {
        String endpoint = eunomiaUrl + "/mail/" + orgId + "/status";
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("x-api-key", eunomiaApiKey);
            HttpEntity<Void> requestEntity = new HttpEntity<>(headers);

            ResponseEntity<MailStatusDTO> response = restTemplate.exchange(
                endpoint,
                HttpMethod.GET,
                requestEntity,
                MailStatusDTO.class
            );

            return response.getBody();
        } catch (Exception e) {
            // Log error and return a default error status
            System.err.println("Error fetching status for orgId " + orgId + ": " + e.getMessage());
            MailStatusDTO errorStatus = new MailStatusDTO();
            errorStatus.setStatus(MailStatus.INACTIVE);
            return errorStatus;
        }
    }

    /**
     * Start the mail pipeline thread for a specific organization.
     *
     * @param orgId The organization ID
     * @param credentials Mail credentials to use
     * @return true if the thread starts successfully, false otherwise
     */
    public boolean startThread(Long orgId, MailThreadRequestDTO credentials) {
        String endpoint = eunomiaUrl + "/mail/" + orgId + "/start";

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("x-api-key", eunomiaApiKey);
            HttpEntity<MailThreadRequestDTO> requestEntity = new HttpEntity<>(credentials, headers);

            ResponseEntity<Void> response = restTemplate.postForEntity(endpoint, requestEntity, Void.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            System.err.println("Error starting thread for orgId " + orgId + ": " + e.getMessage());
            return false;
        }
    }

    /**
     * Stop the mail pipeline thread for a specific organization.
     *
     * @param orgId The organization ID
     * @return true if the thread stops successfully, false otherwise
     */
    public boolean stopThread(Long orgId) {
        String endpoint = eunomiaUrl + "/mail/" + orgId + "/stop";

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("x-api-key", eunomiaApiKey);
            HttpEntity<Void> requestEntity = new HttpEntity<>(headers);

            ResponseEntity<Void> response = restTemplate.exchange(
                endpoint,
                HttpMethod.POST,
                requestEntity,
                Void.class
            );

            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            System.err.println("Error stopping thread for orgId " + orgId + ": " + e.getMessage());
            return false;
        }
    }

    /**
     * Helper method to validate the API key for Eunomia calls.
     *
     * @param apiKey The API key to validate
     * @return true if valid, false otherwise
     */
    public boolean verifyAPIKey(String apiKey) {
        return eunomiaApiKey.equals(apiKey);
    }
}
