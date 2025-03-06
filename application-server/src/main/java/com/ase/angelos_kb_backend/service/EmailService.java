package com.ase.angelos_kb_backend.service;

import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;

@Service
public class EmailService {

    private final JavaMailSender mailSender;

    public EmailService(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    public void sendEmail(String toEmail, String subject, String confirmationUrl) throws MessagingException {
        MimeMessage mimeMessage = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, "UTF-8");
        helper.setTo(toEmail);
        helper.setSubject(subject);
    
        // Using direct hex codes instead of CSS variables.
        String htmlContent = """
            <!DOCTYPE html>
            <html lang="de">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>E-Mail Bestätigen</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        color: #072140;
                        margin: 0;
                        padding: 0;
                    }
                    .email-container {
                        background-color: #ffffff;
                        border: 1px solid #ccc;
                        border-radius: 8px;
                        padding: 20px;
                        max-width: 600px;
                        margin: 40px auto;
                        text-align: center;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }
                    h1 {
                        color: #3070b3;
                    }
                    p {
                        font-size: 14px;
                        margin: 15px 0;
                    }
                    /* Use inline-block and inline styles for the button */
                    a.button {
                        display: inline-block;
                        margin-top: 20px;
                        padding: 10px 15px;
                        background: #3070b3;
                        color: #ffffff !important;
                        text-decoration: none;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    a.button:hover {
                        background: #0a2d57;
                    }
                    a.link {
                        color: #3070b3;
                        text-decoration: none;
                    }
                    a.link:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="email-container">
                    <h1>Angelos - E-Mail Bestätigen</h1>
                    <p>Um Ihre E-Mail-Adresse zu bestätigen, klicken Sie bitte auf den folgenden Button:</p>
                    <a href="%s" class="button">E-Mail bestätigen</a>
                    <p>Falls der Button nicht funktioniert, kopieren Sie bitte den folgenden Link und öffnen Sie ihn in Ihrem Browser:</p>
                    <p><a href="%s" class="link">%s</a></p>
                </div>
            </body>
            </html>
            """.formatted(confirmationUrl, confirmationUrl, confirmationUrl);
    
        helper.setText(htmlContent, true);
        mailSender.send(mimeMessage);
    }
}
