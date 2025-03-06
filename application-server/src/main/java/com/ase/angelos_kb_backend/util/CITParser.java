package com.ase.angelos_kb_backend.util;

import org.springframework.stereotype.Component;

import org.jsoup.Jsoup;
import org.jsoup.nodes.*;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Component
public class CITParser {

    public String parseWebsite(String url) {
        StringBuilder contentText = new StringBuilder();

        try {
            // Fetch the HTML content of the page
            Document doc = Jsoup.connect(url).get();

            // Get the page title
            String pageTitle = doc.title();
            contentText.append(pageTitle).append("\n\n");

            // Select the content div
            Element contentDiv = doc.getElementById("content");

            if (contentDiv == null) {
                System.out.println("Content div not found");
                return "";
            }

            List<Element> childDivs = contentDiv.children();

            int index = 0;
            String pageHeading = "";
            boolean skipFollowingStudyPlans = false;
            Integer previousStartYear = null;

            while (index < childDivs.size()) {
                Element child = childDivs.get(index);

                try {
                    ExtractedData extractedData = getVisibleText(child, pageHeading);
                    String heading = extractedData.getHeading();
                    String text = extractedData.getText();

                    // Make sure only current study plans are included
                    boolean isStudyPlanSection = heading.contains("Studienplan für Studienbeginn") ||
                            heading.contains("Studienplan ab Studienbeginn") ||
                            heading.contains("Studienbeginn ab");

                    if (isStudyPlanSection) {
                        Integer startYear = parseStartYearFromHeading(heading);

                        // Determine if this section should be skipped
                        if (skipFollowingStudyPlans) {
                            if (previousStartYear != null && previousStartYear <= 2019) {
                                // Skip this section because it is older than the cutoff
                                index += 1;
                                continue;
                            } else {
                                previousStartYear = startYear;
                            }
                        } else {
                            previousStartYear = startYear;
                            skipFollowingStudyPlans = true;
                        }
                    } else {
                        // Reset the skip flag if a non-study-plan section is encountered
                        skipFollowingStudyPlans = false;
                    }

                    if (index == 0) {
                        pageHeading = heading;
                    }
                    // Append the extracted content
                    contentText.append(text).append("\n");
                    // Add a separator between different sections
                    contentText.append("\n").append("----------------------------------------").append("\n\n");

                } catch (Exception e) {
                    System.out.println("Could not extract text: " + e.getMessage());
                }

                index += 1;
            }

        } catch (IOException e) {
            System.out.println("Failed to connect to " + url + ": " + e.getMessage());
        }

        return contentText.toString();
    }

    private ExtractedData getVisibleText(Element element, String pageHeading) {
        // Prepare containers for the output
        List<String> content = new ArrayList<>();
        Deque<Heading> hierarchyStack = new ArrayDeque<>();
        if (!pageHeading.isEmpty()) {
            hierarchyStack.push(new Heading(pageHeading, 1));
        }
        String sectionHeading = "";

        // Set up list to track all table texts to avoid duplicates
        List<String> tableTexts = new ArrayList<>();

        // Process all elements within the child div
        Elements elements = element.getAllElements();
        for (Element elem : elements) {
            String tagName = elem.tagName().toLowerCase();

            if (tagName.matches("h[1-6]")) { // Handle headings (h1, h2, h3, ...)
                String headingText = elem.text().trim();
                int headingLevel = Integer.parseInt(tagName.substring(1)); // Extract the level from the tag name (e.g., 'h2' -> 2)

                // Get first heading specific to section
                if (sectionHeading.isEmpty()) {
                    sectionHeading = headingText;
                }

                while (!hierarchyStack.isEmpty() && hierarchyStack.peek().getLevel() >= headingLevel) {
                    hierarchyStack.pop();
                }

                // Add the new heading to the stack
                hierarchyStack.push(new Heading(headingText, headingLevel));

                // Build the hierarchical string
                List<Heading> hierarchyList = new ArrayList<>(hierarchyStack);
                Collections.reverse(hierarchyList);
                String hierarchyString = hierarchyList.stream()
                        .map(Heading::toString)
                        .collect(Collectors.joining(" > "));
                content.add("\n" + headingText);
                content.add(hierarchyString);

            } else if (tagName.equals("p")) { // Handle paragraphs
                String paragraphText = elem.text().trim();
                if (!paragraphText.isEmpty() && tableTexts.stream().noneMatch(t -> t.contains(paragraphText))) {
                    content.add(paragraphText);
                }

            } else if (tagName.equals("li")) { // Handle list items
                String listItemText = elem.text().trim();
                if (!listItemText.isEmpty() && tableTexts.stream().noneMatch(t -> t.contains(listItemText))) {
                    content.add("- " + listItemText);
                }

            } else if (tagName.equals("table")) { // Handle tables
                List<Heading> hierarchyList = new ArrayList<>(hierarchyStack);
                Collections.reverse(hierarchyList);
                String hierarchyString = hierarchyList.stream()
                        .map(Heading::toString)
                        .collect(Collectors.joining(" > "));
                String tableHeading = "Table (" + hierarchyString + "):";
                String tableText = processTable(elem);
                content.add(tableHeading + "\n" + tableText + "\n");
                tableTexts.add(tableText);
            }
        }

        String fullText = content.stream().collect(Collectors.joining("\n")).trim();

        return new ExtractedData(sectionHeading, fullText);
    }

    private String processTable(Element tableElement) {
        List<String> rows = new ArrayList<>();

        // Process the header (if any)
        Elements theads = tableElement.select("thead");
        if (!theads.isEmpty()) {
            Elements headers = theads.select("tr");
            for (Element header : headers) {
                List<String> rowData = new ArrayList<>();
                Elements ths = header.select("th");
                for (Element th : ths) {
                    String cellText = th.text().trim();
                    rowData.add(cellText.isEmpty() ? " " : cellText);
                }
                rows.add(String.join(" | ", rowData));
            }
        }

        // Process all the rows in the body
        Elements bodyRows = tableElement.select("tbody tr");
        for (Element row : bodyRows) {
            List<String> rowData = new ArrayList<>();
            Elements cells = row.select("td");
            for (Element cell : cells) {
                // Check if the cell contains a link
                Elements links = cell.select("a");
                String cellText;
                if (!links.isEmpty()) {
                    Element link = links.first();
                    cellText = link.text() + " (" + link.attr("href") + ")";
                } else {
                    cellText = cell.text();
                }
                cellText = cellText.trim();
                rowData.add(cellText.isEmpty() ? " " : cellText);
            }
            rows.add(String.join(" | ", rowData));
        }

        // Combine all rows into a single string with line breaks
        String tableText = String.join("\n", rows);
        return tableText;
    }

    private Integer parseStartYearFromHeading(String heading) {
        // Define a regex pattern to capture the first four-digit year
        Pattern yearPattern = Pattern.compile("\\b(\\d{4})\\b");

        // Search for the first occurrence of a four-digit year in the heading
        Matcher matcher = yearPattern.matcher(heading);
        if (matcher.find()) {
            // Return the year as an integer
            return Integer.parseInt(matcher.group(1));
        }

        return null;
    }

    // Helper Classes
    private static class Heading {
        private String text;
        private int level;

        public Heading(String text, int level) {
            this.text = text;
            this.level = level;
        }

        public int getLevel() {
            return level;
        }

        public String toString() {
            return text;
        }
    }

    private static class ExtractedData {
        private String heading;
        private String text;

        public ExtractedData(String heading, String text) {
            this.heading = heading;
            this.text = text;
        }

        public String getHeading() {
            return heading;
        }

        public String getText() {
            return text;
        }
    }
}