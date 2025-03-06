# studi.chat

<p align="center">
  <img src="assets/studi-chat-logo2.png" alt="studi.chat Logo" height="280">
</p>

## 📌 Overview

**studi.chat** is an AI-powered solution designed to **enhance communication between students and academic advisory services**. It leverages **Retrieval-Augmented Generation (RAG)** to provide **accurate, real-time responses** to student inquiries, reducing the workload on advisors and improving response efficiency.

Modern educational institutions face **increasing administrative complexity** as organizational complexity and student populations grow. Many inquiries are **repetitive and routine**, yet they require significant time from academic staff. **studi.chat** addresses this challenge by automating responses through a **chatbot interface and an intelligent email response system**, while ensuring **advisors maintain full control** over the system’s knowledge base.

## 🚀 Key Features

- **AI-Powered Responses** – Uses RAG to generate contextually relevant answers.
- **Chatbot Interface** – Allows students to ask questions and receive instant responses.
- **Automated Email Handling** – Classifies emails and automates responses to routine inquiries.
- **Knowledge Base Management** – Advisors can update information to ensure responses remain accurate.
- **Seamless Integration** – Designed to integrate smoothly with existing academic support workflows.
- **Scalable & Extensible** – Modular architecture allows for easy expansion and customization.

## 🏗 System Architecture

The system is composed of several key components:

- **Chatbot UI** – A modern web-based chatbot interface for student interaction.
- **Knowledge Manager UI** – A web-based interface for advisors to manage documents, resources, and system settings.
- **Application Server** – A Java-based backend (Spring Boot) that connects all system components.
- **RAG System** – A FastAPI-based microservice that retrieves and generates answers using a Weaviate vector database.
- **Email Response System** – Automates email replies, filtering sensitive messages while sending out email responses to routine inquiries.
- **Reverse Proxy** – Ensures secure and efficient routing of traffic.

## 🏆 Why studi.chat?

- **Reduces Administrative Overload** – Frees up valuable time for academic advisors to focus on complex cases.
- **Enhances Student Experience** – Provides instant, reliable answers to students’ questions.
- **Ensures Information Accuracy** – Easily updated knowledge base to keep responses aligned with institutional policies.
- **Data Privacy & Security** – No sensitive data storage. Can be deployed on-premise or in a secure cloud environment.
- **Customizable & Scalable** – Adaptable to different institutions and workflows.

---