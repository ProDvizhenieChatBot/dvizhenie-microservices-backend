# Project Roadmap

This document provides a high-level overview of the development phases for the charity fund's backend system. It outlines the major strategic goals for each phase.

For detailed, actionable tasks, please refer to the team's `kanban.md`. The technical contract for the API is defined in the `openapi.yaml` specification.

---

### **Phase 1: Foundational Setup [Completed]**

The goal of this phase was to establish the project's infrastructure and build the initial, isolated versions of each service. This phase is complete.

*   **Microservice Architecture:** The project was structured with three core services (`api-service`, `bot-service`, `file-storage-service`) and an Nginx `gateway`. All services are containerized with Docker.
*   **File Storage Service:** A fully functional service for uploading files to MinIO (S3) and generating secure download links was implemented.
*   **Initial API Endpoints:** Basic, proof-of-concept endpoints for creating and updating applications were developed.

---

### **Phase 2: Core Logic Refactoring and Admin Features [In Progress]**

This is the current and most critical phase. The goal is to refactor the data model to support the full requirements of the application lifecycle and to build the necessary API endpoints for both users and administrators.

*   **Implement Admin Authentication (MVP):**
    *   Secure all administrative endpoints using **Nginx Basic Auth**. This provides a simple and effective security layer for the MVP, with credentials managed via environment variables.

*   **Refactor the Core Data Model:**
    *   The `Application` model is being rebuilt to use **UUIDs as primary keys** for secure, public-facing links.
    *   Support for **resumable sessions** will be added by linking applications to a user's `telegram_id`.
    *   A dedicated `ApplicationFile` table will be created to properly link uploaded files to their corresponding applications and form fields.

*   **Develop Admin API Endpoints:**
    *   Create secure endpoints for foundation staff to list, view, and change the status of applications. These endpoints will operate on the new UUID-based data model.

*   **Develop Public API for Mini App:**
    *   Implement the public-facing endpoints that the Mini App will use. This includes saving form progress, linking uploaded files, and submitting the final application, all identified by the application's **UUID in the URL** (e.g., `PATCH /applications/{application_uuid}`).

*   **Make Form Schema Database-Backed:**
    *   Transition the application form structure from a static JSON file to a model in the database to allow for future management without code changes.

---

### **Phase 3: Client Integration and Finalization [Next Up]**

This phase will focus on connecting the client-facing services to the stable backend and preparing for launch.

*   **Finalize Bot Service Integration:**
    *   Connect the `bot-service` to the refactored `api-service`. The bot will use the new `telegram_id`-based logic to create or resume user sessions, providing a seamless experience for returning users.

*   **End-to-End Testing:**
    *   Conduct comprehensive testing of the full user journey: from a user starting a dialogue in Telegram to an admin processing the completed application.

*   **Implement Web Widget Support (Future):**
    *   Develop the session logic for users initiating the process from the foundation's website, likely using a "Magic Link" approach.