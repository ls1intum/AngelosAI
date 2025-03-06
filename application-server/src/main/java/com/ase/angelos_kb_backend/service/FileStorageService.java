package com.ase.angelos_kb_backend.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.util.UUID;

@Service
public class FileStorageService {

    private final Path fileStorageLocation;

    public FileStorageService(@Value("${file.upload-dir}") String uploadDir) {
        this.fileStorageLocation = Paths.get(uploadDir).toAbsolutePath().normalize();

        try {
            Files.createDirectories(this.fileStorageLocation);
        } catch (IOException ex) {
            throw new RuntimeException("Could not create the directory where uploaded files will be stored.", ex);
        }
    }

    /**
     * Store a file in the storage location, ensuring the filename is unique.
     */
    public String storeFile(MultipartFile file, String filename) {
        int attempts = 0;
        Path targetLocation;
        try {
            do {
                // Ensure directory traversal attacks are prevented
                if (filename.contains("..")) {
                    throw new RuntimeException("Filename contains invalid path sequence: " + filename);
                }
                targetLocation = this.fileStorageLocation.resolve(filename);

                if (Files.exists(targetLocation)) {
                    // Generate a new filename if conflict occurs
                    filename = UUID.randomUUID().toString() + ".pdf";
                }
                attempts++;
                if (attempts > 10) {
                    throw new RuntimeException("Could not store file " + filename + ". Please try again!");
                }
            } while (Files.exists(targetLocation));

            // Save the file
            Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);

            return filename;

        } catch (IOException ex) {
            throw new RuntimeException("Could not store file " + filename + ". Please try again!", ex);
        }
    }

    /**
     * Load file as a resource.
     */
    public Path loadFile(String filename) {
        return this.fileStorageLocation.resolve(filename).normalize();
    }

    /**
     * Delete a file.
     */
    public void deleteFile(String filename) {
        try {
            Path filePath = this.fileStorageLocation.resolve(filename).normalize();
            Files.deleteIfExists(filePath);
        } catch (IOException ex) {
            throw new RuntimeException("Could not delete file " + filename, ex);
        }
    }
}
