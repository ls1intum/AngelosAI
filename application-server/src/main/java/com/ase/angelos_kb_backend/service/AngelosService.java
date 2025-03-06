package com.ase.angelos_kb_backend.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.lang.Nullable;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import com.ase.angelos_kb_backend.dto.DocumentDataDTO;
import com.ase.angelos_kb_backend.dto.SampleQuestionDTO;
import com.ase.angelos_kb_backend.dto.angelos.AngelosAddDocumentRequest;
import com.ase.angelos_kb_backend.dto.angelos.AngelosAddSampleQuestionRequest;
import com.ase.angelos_kb_backend.dto.angelos.AngelosAddWebsiteRequest;
import com.ase.angelos_kb_backend.dto.angelos.AngelosChatRequest;
import com.ase.angelos_kb_backend.dto.angelos.AngelosChatResponse;
import com.ase.angelos_kb_backend.dto.angelos.AngelosEditDocumentRequest;
import com.ase.angelos_kb_backend.dto.angelos.AngelosEditSampleQuestionRequest;
import com.ase.angelos_kb_backend.dto.angelos.AngelosEditWebsiteRequest;
import com.ase.angelos_kb_backend.dto.angelos.AngelosRefreshContentRequest;
import com.ase.angelos_kb_backend.dto.eunomia.MailResponseRequestDTO;

@Component
public class AngelosService {

    @Value("${angelos.url}")
    private String angelosUrl;

    @Value("${angelos.secret}")
    private String angelosSecret;

    private final RestTemplate restTemplate;

    public AngelosService() {
        this.restTemplate = new RestTemplate();
    }

    public boolean verifyAPIKey(String secret) {
        return secret.equals(angelosSecret);
    }

    /**
     * Forwards an chat request from the chatbot to the RAG
     */
    public AngelosChatResponse sendChatMessage(AngelosChatRequest request, boolean filterByOrg) {
        String endpoint = angelosUrl + "/v1/question/chat?filterByOrg=" + filterByOrg;
    
        HttpHeaders headers = new HttpHeaders();
        headers.set("x-api-key", angelosSecret);
    
        // Only the original request body is sent, without filterByOrg
        HttpEntity<AngelosChatRequest> requestEntity = new HttpEntity<>(request, headers);
    
        ResponseEntity<AngelosChatResponse> response = 
            restTemplate.postForEntity(endpoint, requestEntity, AngelosChatResponse.class);
    
        return response.getBody();
    }

    /**
     * Forwards an response request from the mail pipeline to the RAG
     */
    public AngelosChatResponse sendAskRequest(MailResponseRequestDTO request) {
        String endpoint = angelosUrl + "/v1/question/ask";

        HttpHeaders headers = new HttpHeaders();
        headers.set("x-api-key", angelosSecret);

        // Wrap the request in an HttpEntity
        HttpEntity<MailResponseRequestDTO> requestEntity = new HttpEntity<>(request, headers);

        // Make the POST call
        ResponseEntity<AngelosChatResponse> response =
            restTemplate.postForEntity(endpoint, requestEntity, AngelosChatResponse.class);

        return response.getBody();
    }

    /**
     * Send a request to add a website resource to the Angelos RAG system.
     */
    public boolean sendWebsiteAddRequest(AngelosAddWebsiteRequest request) {
        String endpoint = angelosUrl + "/knowledge/website/add";
        return sendPostRequest(endpoint, request);
    }

    /**
     * Send a batch request to add multiple websites to the Angelos RAG system.
     */
    public boolean sendBatchWebsiteAddRequest(List<AngelosAddWebsiteRequest> requests) {
        String endpoint = angelosUrl + "/knowledge/website/addBatch";
        return sendPostRequest(endpoint, requests);
    }

    /**
     * Send a request to update an existing website's content.
     */
    public boolean sendWebsiteRefreshRequest(String id, String content) {
        AngelosRefreshContentRequest body = new AngelosRefreshContentRequest();
        body.setContent(content);

        String endpoint = angelosUrl + "/knowledge/website/" + id + "/refresh";
        return sendPostRequest(endpoint, body);
    }

    /**
     * Send a request to update a website's title and study programs.
     */
    public boolean sendWebsiteUpdateRequest(String id, String title, List<String> studyPrograms, Long orgId) {
        AngelosEditWebsiteRequest body = new AngelosEditWebsiteRequest();
        body.setTitle(title);
        body.setStudyPrograms(studyPrograms);
        body.setOrgId(orgId);

        String endpoint = angelosUrl + "/knowledge/website/" + id + "/update";
        return sendPostRequest(endpoint, body);
    }

    /**
     * Send a request to delete a website from Angelos.
     */
    public boolean sendWebsiteDeleteRequest(String id) {
        String endpoint = angelosUrl + "/knowledge/website/" + id + "/delete";
        return sendDeleteRequest(endpoint, null);
    }

    /**
     * Send a request to batch delete websites from Angelos.
     */
    public boolean sendWebsiteBatchDeleteRequest(List<String> ids) {
        if (ids.size() == 0) return true;
        String endpoint = angelosUrl + "/knowledge/website/deleteBatch";
        return sendDeleteRequest(endpoint, ids);
    }

    /**
     * Send a request to add a document resource.
     */
    public boolean sendDocumentAddRequest(DocumentDataDTO doc, String content, Long orgId) {
        AngelosAddDocumentRequest body = new AngelosAddDocumentRequest();
        body.setId(doc.getId());
        body.setOrgId(orgId);
        body.setTitle(doc.getTitle());
        body.setStudyPrograms(doc.getStudyPrograms().stream().map(sp -> sp.getName()).toList());
        body.setContent(content);

        String endpoint = angelosUrl + "/knowledge/document/add";
        return sendPostRequest(endpoint, body);
    }

    /**
     * Send a request to update an existing document's content.
     */
    public boolean sendDocumentRefreshRequest(String id, String content) {
        AngelosRefreshContentRequest body = new AngelosRefreshContentRequest();
        body.setContent(content);

        String endpoint = angelosUrl + "/knowledge/document/" + id + "/refresh";
        return sendPostRequest(endpoint, body);
    }

    /**
     * Send a request to edit a document resource.
     */
    public boolean sendDocumentEditRequest(DocumentDataDTO doc, Long orgId) {
        AngelosEditDocumentRequest body = new AngelosEditDocumentRequest();
        body.setTitle(doc.getTitle());
        body.setStudyPrograms(doc.getStudyPrograms().stream().map(sp -> sp.getName()).toList());
        body.setOrgId(orgId);

        String endpoint = angelosUrl + "/knowledge/document/" + doc.getId() + "/edit";
        return sendPostRequest(endpoint, body);
    }

    /**
     * Send a request to delete a document resource.
     */
    public boolean sendDocumentDeleteRequest(String id) {
        String endpoint = angelosUrl + "/knowledge/document/" + id + "/delete";
        return sendDeleteRequest(endpoint, null);
    }

    /**
     * Send a request to batch delete document resources.
     */
    public boolean sendDocumentBatchDeleteRequest(List<String> ids) {
        if (ids.size() == 0) return true;
        String endpoint = angelosUrl + "/knowledge/document/deleteBatch";
        return sendDeleteRequest(endpoint, ids);
    }

    /**
     * Send a request to add a sample question resource.
     */
    public boolean sendSampleQuestionAddRequest(SampleQuestionDTO sampleQuestion, Long orgId) {
        AngelosAddSampleQuestionRequest body = new AngelosAddSampleQuestionRequest();
        body.setId(sampleQuestion.getId());
        body.setOrgId(orgId);
        body.setTopic(sampleQuestion.getTopic());
        body.setQuestion(sampleQuestion.getQuestion());
        body.setAnswer(sampleQuestion.getAnswer());
        body.setStudyPrograms(sampleQuestion.getStudyPrograms().stream().map(sp -> sp.getName()).toList());

        String endpoint = angelosUrl + "/knowledge/sample-question/add";
        return sendPostRequest(endpoint, body);
    }

    /**
     * Send a batch request to add multiple sample questions to the Angelos RAG system.
     */
    public boolean sendBatchSampleQuestionAddRequest(List<AngelosAddSampleQuestionRequest> requests) {
        String endpoint = angelosUrl + "/knowledge/sample-question/addBatch";
        return sendPostRequest(endpoint, requests);
    }

    /**
     * Send a request to edit a sample question resource.
     */
    public boolean sendSampleQuestionEditRequest(SampleQuestionDTO sampleQuestion, Long orgId) {
        AngelosEditSampleQuestionRequest body = new AngelosEditSampleQuestionRequest();
        body.setTopic(sampleQuestion.getTopic());
        body.setQuestion(sampleQuestion.getQuestion());
        body.setAnswer(sampleQuestion.getAnswer());
        body.setStudyPrograms(sampleQuestion.getStudyPrograms().stream().map(sp -> sp.getName()).toList());
        body.setOrgId(orgId);

        String endpoint = angelosUrl + "/knowledge/sample-question/" + sampleQuestion.getId() + "/edit";
        return sendPostRequest(endpoint, body);
    }

    /**
     * Send a request to delete a sample question resource.
     */
    public boolean sendSampleQuestionDeleteRequest(String id) {
        String endpoint = angelosUrl + "/knowledge/sample-question/" + id + "/delete";
        return sendDeleteRequest(endpoint, null);
    }

    /**
     * Send a request to batch delete sample question resources.
     */
    public boolean sendSampleQuestionBatchDeleteRequest(List<String> ids) {
        if (ids.size() == 0) return true;
        String endpoint = angelosUrl + "/knowledge/sample-question/deleteBatch";
        return sendDeleteRequest(endpoint, ids);
    }


    /**
     * Helper method to send POST requests and return boolean based on success.
     */
    private boolean sendPostRequest(String endpoint, Object body) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("x-api-key", angelosSecret);
            HttpEntity<Object> requestEntity = new HttpEntity<>(body, headers);
            ResponseEntity<Void> response = restTemplate.postForEntity(endpoint, requestEntity, Void.class);
            
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            System.err.println("Error sending request: " + e.getMessage());
            return false;
        }
    }

    /**
     * Helper method to send DELETE requests with an optional body.
     */
    private boolean sendDeleteRequest(String endpoint, @Nullable Object body) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("x-api-key", angelosSecret);
            
            HttpEntity<Object> requestEntity = (body != null) ? new HttpEntity<>(body, headers) : new HttpEntity<>(headers);

            restTemplate.exchange(endpoint, HttpMethod.DELETE, requestEntity, Void.class);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}