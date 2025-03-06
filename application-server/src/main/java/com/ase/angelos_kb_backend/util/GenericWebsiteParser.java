package com.ase.angelos_kb_backend.util;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.nodes.Node;
import org.springframework.stereotype.Component;


@Component
public class GenericWebsiteParser {

    public String parseWebsiteContent(String url) {
        // Extract content using Jsoup
        String jsoupContent = extractWithJsoup(url);
        return jsoupContent;
    }

    // Truncation of website content specific to TUM websites
    public String truncateString(String s) {
        // Define the substrings to search for
        String[] substrings = {"TYPO3SEARCH_end", "studium spam prevention @tum.de"};
    
        // Initialize a list to hold the last indices of each substring
        List<Integer> lastIndices = new ArrayList<>();
    
        // Iterate over each substring and find its last occurrence
        for (String substr : substrings) {
            int index = s.lastIndexOf(substr);
            if (index != -1) {
                lastIndices.add(index);
            }
        }
    
        if (!lastIndices.isEmpty()) {
            // Truncate at the last occurrence of any specified substring
            int truncateIndex = Collections.max(lastIndices);
            s = s.substring(0, truncateIndex);
        }
    
        // Remove lines starting with "window.flow"
        String[] lines = s.split("\\R");
        StringBuilder filteredLines = new StringBuilder();
        for (String line : lines) {
            if (!line.trim().startsWith("window.flow")) {
                filteredLines.append(line).append("\n");
            }
        }
    
        // Return the filtered content (full content if no substrings were found)
        return filteredLines.toString();
    }

    // Extract content from a URL using Jsoup, structuring the text with hierarchy
    public String extractWithJsoup(String url) {
        try {
            // Fetch the URL
            org.jsoup.Connection.Response response = Jsoup.connect(url).timeout(10_000).userAgent("Mozilla/5.0").execute();
    
            if (response.statusCode() == 200) {
                String htmlContent = response.body();
    
                // Parse the entire content by default
                Document document = Jsoup.parse(htmlContent);
    
                // If marker is found, process only the content after the marker
                int markerPos = htmlContent.indexOf("TYPO3SEARCH_begin");
                if (markerPos != -1) {
                    String contentAfterMarker = htmlContent.substring(markerPos + "TYPO3SEARCH_begin".length());
                    document = Jsoup.parse(contentAfterMarker);
                }
    
                // Initialize a list to hold the structured text
                List<String> content = new ArrayList<>();
    
                // Start processing from the root of the parsed content
                processElement(document, content, 0);
    
                // Join the content
                String structuredText = String.join("\n", content);
    
                // Remove extra newlines
                structuredText = structuredText.replaceAll("\\n\\n", "\n");
                structuredText = structuredText.replaceAll("\\n{3,}", "\n\n");
    
                // Apply truncation if necessary, otherwise return the structured content
                return truncateString(structuredText.trim());
    
            } else {
                System.out.println("Failed to extract content from " + url + " with Jsoup. Status Code: " + response.statusCode());
                return null;
            }
        } catch (IOException e) {
            System.out.println("Failed to extract content from " + url + " with Jsoup. Exception: " + e.getMessage());
            return null;
        }
    }

    // Recursive function to process elements
    public void processElement(Node node, List<String> content, int level) {
        for (Node child : node.childNodes()) {
            if (child instanceof org.jsoup.nodes.TextNode) {
                String text = ((org.jsoup.nodes.TextNode) child).text().trim();
                if (!text.isEmpty()) {
                    // Ensure proper whitespace handling
                    if (!content.isEmpty() && !content.get(content.size() - 1).endsWith("\n")) {
                        // Append to the last line with a space
                        int lastIndex = content.size() - 1;
                        content.set(lastIndex, content.get(lastIndex) + " " + text);
                    } else {
                        content.add(repeat(" ", level) + text);
                    }
                }
            } else if (child instanceof Element) {
                Element childElement = (Element) child;
                String tagName = childElement.tagName();

                if (tagName.matches("h[1-6]")) {
                    // Headings: add new line and appropriate indentation
                    int headingLevel = Integer.parseInt(tagName.substring(1));
                    String indent = repeat(" ", (headingLevel - 1) * 4); // Indent based on heading level
                    String headingText = childElement.text().trim();
                    content.add("\n" + indent + headingText + "\n");
                } else if (tagName.equals("p")) {
                    // Paragraphs
                    String paragraphText = childElement.text().trim();
                    if (!paragraphText.isEmpty()) {
                        content.add(repeat(" ", level) + paragraphText + "\n");
                    }
                } else if (tagName.equals("ul") || tagName.equals("ol")) {
                    // Lists
                    for (Element li : childElement.select("> li")) {
                        String liText = li.text().trim();
                        content.add(repeat(" ", level + 2) + "- " + liText);
                    }
                } else {
                    // Other tags: process recursively
                    processElement(childElement, content, level);
                }
            }
        }
    }

    // Helper method to repeat a string
    public String repeat(String s, int times) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < times; i++) {
            sb.append(s);
        }
        return sb.toString();
    }
}
