package com.ase.angelos_kb_backend.service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import com.ase.angelos_kb_backend.util.CITParser;
import com.ase.angelos_kb_backend.util.GenericWebsiteParser;
import com.ase.angelos_kb_backend.util.ParseResult;

@Component
public class ParsingService {
    private CITParser citParser;
    private GenericWebsiteParser websiteParser;

    public ParsingService(CITParser citParser, GenericWebsiteParser websiteParser) {
        this.citParser = citParser;
        this.websiteParser = websiteParser;
    }

    // Parse website content
    public ParseResult parseWebsite(String link) {
        String result;
        String type;
        if (link.contains("cit.tum.de")) {
            result = citParser.parseWebsite(link);
            type = "CIT";
        } else {
            // Use generic parser for other links
            result = websiteParser.parseWebsiteContent(link);
            type = "other";
        }

        return new ParseResult(result, type);
    }

    public String parseDocument(MultipartFile file) {
        try {
            // Load PDF using Loader
            byte[] fileBytes = file.getBytes();
            try (PDDocument document = Loader.loadPDF(fileBytes)) {
                PDFTextStripper stripper = new PDFTextStripper();
                // Extract text for the entire document
                String result = stripper.getText(document);
                return result;
            } catch (IOException e) {
                throw new RuntimeException("Failed to parse PDF document", e);
            }
        } catch (IOException e) {
            throw new RuntimeException("Failed to read PDF file", e);
        }
    }

    /**
     * Compute a SHA-256 content hash for the given input.
     * 
     * @param content the input content to hash
     * @return the SHA-256 hash of the content encoded in Base64
     */
    public String computeContentHash(String content) {
        try {
            // Get a SHA-256 MessageDigest instance
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            
            // Compute the hash
            byte[] hashBytes = digest.digest(content.getBytes(StandardCharsets.UTF_8));
            
            // Encode the hash as a Base64 string for readability and storage
            return Base64.getEncoder().encodeToString(hashBytes);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("Hashing algorithm not available", e);
        }
    }
}

