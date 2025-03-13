# AngelosAI

<p align="center">
  <img src="assets/angelos-ai-logo2.png" alt="studi.chat Logo" height="280">
</p>

## 📌 Overview

**AngelosAI** is an AI-powered solution designed to **enhance communication between students and academic advisory services** at **TUM School of Computation, Information, and Technology (CIT)**. It leverages **Retrieval-Augmented Generation (RAG)** to provide **accurate, real-time responses** to student inquiries, reducing the workload on advisors and improving response efficiency.

At TUM CIT, academic advisory services face an increasing number of repetitive student inquiries—often related to examinations, study plans, credit recognition, and administrative processes. These routine requests consume valuable time that could be better spent on complex student cases requiring personal guidance. **AngelosAI** addresses this challenge by automating responses through a **chatbot interface and an intelligent email response system**, while ensuring **advisors maintain full control** over the system’s knowledge base.

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

## 🏆 Success Criteria

- **Reduces Administrative Overload** – Frees up valuable time for academic advisors to focus on complex cases.
- **Enhances Student Experience** – Provides instant, reliable answers to students’ questions.
- **Ensures Information Accuracy** – Easily updated knowledge base to keep responses aligned with institutional policies.
- **Data Privacy & Security** – No sensitive data storage. Can be deployed on-premise or in a secure cloud environment.
- **Customizable & Scalable** – Adaptable to different institutions and workflows.

## ⚙️ Local Setup  
### 1️⃣ Prerequisites  
- Install **Docker** and **Docker Compose**.  

### 2️⃣ Environment Configuration  
- RAG, mail system and application server require an **environment file (`development.env`)**. In the application-server directory, a `posgres.env` file should be defined.
- **Template files (`template.env`)** are available in the respective project folders.

### 3️⃣ Start Docker Services  
Run the following command in the **root project folder**:  
```sh
docker compose -f docker-compose.local.yml up --build
```

### 4️⃣ Admin Login & User Registration
- The Knowledge Manager is available at http://localhost/knowledge-manager/
- Log in as system admin using credentials from development.env (Application Server).
- You can create an Organization in the Administration tab.
-	The organization ID specified in ./chatbot-ui/src/environments/environment.development.ts determines which organization’s knowledge base the chatbot uses for generating responses.
-	New users must register and be approved by a (system) admin before gaining access.

### 5️⃣ Database Initialization
- The knowledge base of a organisation can be initialized using the Knowledge Manager UI
- The init-db endpoint initializes the database for CIT advising given that the necessary study programs are added and the method is called by a system admin.
