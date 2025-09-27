# Project Roadmap

This document provides a high-level overview of the development phases for the charity fund's backend system. The initial project setup and microservice architecture are complete.

For detailed, actionable tasks, please refer to the team's Kanban board. The technical contract for the API is defined in the `openapi.yaml` specification.

---

### **Phase 1: Core Backend Implementation**

The goal of this phase is to build the foundational logic for handling applications, files, and administrative access.

*   **Implement Application Lifecycle:**
    *   Develop the primary API endpoints for creating application drafts, saving progress (`PATCH /applications/me`), and retrieving application data for the Mini App.

*   **Implement Admin Authentication via Yandex OAuth 2.0:**
    *   Integrate a secure and standard authentication process for foundation staff using their Yandex accounts. This includes handling the OAuth flow and issuing internal JWTs for session management.

*   **Build out the File Storage Service:**
    *   Implement the file upload logic with S3 (MinIO) integration.
    *   Develop the functionality to generate secure, temporary (pre-signed) URLs for downloading documents.
    *   Establish a link between uploaded files and the applications they belong to.

---

### **Phase 2: Admin Panel and Schema Management**

This phase focuses on providing tools for foundation staff to manage the system effectively.

*   **Develop Admin API Endpoints:**
    *   Create secure endpoints for listing, viewing, and changing the status of applications.
    *   Implement filtering and pagination for managing a large number of applications.

*   **Make Form Schema Database-Backed:**
    *   Transition the application form structure from a static file to a model in the database.
    *   Create secure administrative endpoints for viewing and eventually managing different versions of the application form.

---

### **Phase 3: Client Integration and Finalization**

This phase ensures that the client-facing services (like the Telegram Bot) are fully integrated and the system is ready for use.

*   **Finalize Bot Service Integration:**
    *   Connect the `bot-service` to the production-ready session creation and notification endpoints of the `api-service`.

*   **Implement Web Widget Support (Future):**
    *   Develop the "Magic Link" session logic for users initiating the process from the foundation's website.

*   **End-to-End Testing:**
    *   Conduct comprehensive testing of the full user journey: from a user starting a dialogue in Telegram to an admin processing the application in the admin panel.