### **Phase 1: Implement Core API Service Logic**

This is the highest priority phase, as all other services depend on a functional API.

*   **Task 1.1: Implement Application Endpoints.**
    *   `[ ]` **Create Application:** Implement `POST /applications` to create a new application entry in the database.
    *   `[ ]` **Update Application:** Implement `PATCH /applications/{id}` to save partial form data, allowing users to continue later.
    *   `[ ]` **Get Application:** Implement `GET /applications/{id}` for a user to retrieve their application data using a session token.
    *   `[ ]` **Admin Endpoints:** Implement secure endpoints for admins to list, view, and manage the status of all applications.

*   **Task 1.2: Implement Session & Authentication Logic.**
    *   `[ ]` **Telegram Sessions:** Enhance `POST /sessions/telegram`. Instead of returning a random token, it should create a draft `Application` in the database and return a JWT or secure token associated with that draft.
    *   `[ ]` **Admin Authentication:** Implement OAuth2 (e.g., Password Flow) on the `/auth` endpoints to secure the admin panel and endpoints.

*   **Task 1.3: Make Form Schema Database-Backed.**
    *   `[ ]` **Create DB Model:** Add a `FormSchema` model to `db_models.py` to store form schemas in the database.
    *   `[ ]` **Create Alembic Migration:** Generate a new migration to create the `form_schemas` table.
    *   `[ ]` **Update Endpoint Logic:** Modify the `GET /forms/schema/active` endpoint to fetch the latest active schema from the database instead of the static JSON file.
    *   `[ ]` **Implement Admin CRUD for Schemas:** Create secure endpoints for administrators to create, view, and update form schemas.

---

### **Phase 2: Build Out File Storage Service**

This phase involves integrating the file service with a real object storage backend (MinIO).

*   **Task 2.1: Integrate S3 Client.**
    *   `[ ]` Add and configure an S3 client library (e.g., `boto3`) to connect to the MinIO container using credentials from environment variables.
    *   `[ ]` Create a utility/client to initialize the MinIO bucket (`charity-files`) on service startup if it doesn't exist.

*   **Task 2.2: Implement File Upload Logic.**
    *   `[ ]` In the `POST /files/` endpoint, implement the logic to stream the `UploadFile` content directly to the MinIO bucket.
    *   `[ ]` Store metadata about the file (e.g., original filename, owner, application ID) in the PostgreSQL database via the API service.

*   **Task 2.3: Implement Pre-signed URL Generation.**
    *   `[ ]` In the `GET /files/{file_id}/download-link` endpoint, implement the logic to generate a temporary, secure, pre-signed URL for the requested file from MinIO.

---

### **Phase 3: Finalize Bot and Implement Web Support**

With the backend services functional, the client-facing parts can be fully implemented.

*   **Task 3.1: Refine Bot Service Integration.**
    *   `[ ]` Update the `/start` command handler in `bot_service` to correctly use the now-functional session creation endpoint from the `api_service`.
    *   `[ ]` Implement the internal `/notify` endpoint in the bot, which can be called by the `api_service` to send status updates to users (e.g., "Your application has been received").

*   **Task 3.2: Implement Web Widget Session Logic.**
    *   `[ ]` Implement the "Magic Link" logic in `POST /sessions/web` in the `api_service`.
    *   `[ ]` This will require integrating an email-sending library/service to send a unique login link to the user's email address.

---

### **Phase 4: Testing and Finalization**

The final phase involves ensuring all parts of the system work together correctly.

*   `[ ]` **End-to-End Testing:** Perform comprehensive testing of all user flows:
    *   Filling out and submitting an application via the Telegram Mini App.
    *   Uploading and downloading documents.
    *   Admin viewing and managing applications.
*   `[ ]` **Review and Refactor:** Clean up code, add missing documentation, and optimize where necessary.
*   `[ ]` **Prepare for Deployment:** Finalize production configurations and write deployment instructions.