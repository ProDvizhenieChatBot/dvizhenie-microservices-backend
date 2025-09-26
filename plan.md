### **Phase 1: Foundation & Project Restructuring**
*   **Task 1.1: Create New Directory Structure.**
    *   Create the `services/` directory.
    *   Create subdirectories for `api_service`, `bot_service`, and `file_storage_service`.
    *   Move relevant code from the old monolith `src/` into the new service directories as a starting point.
*   **Task 1.2: Update `docker-compose.yml`.**
    *   Implement the new `docker-compose.yml` with all services defined.
    *   Configure the database and the new MinIO service.
*   **Task 1.3: Create Dockerfiles & Basic Apps.**
    *   Create a `Dockerfile` and a minimal "Hello World" FastAPI app inside each service directory to ensure the orchestration works and services can communicate.
*   **Task 1.4: Configure API Gateway (NGINX).**
    *   Set up the basic `nginx.conf` with routing rules to the new services.

### **Phase 2: Core Logic Migration (API Service)**
*   **Task 2.1: Migrate Database Models & Alembic.**
    *   Move `db_models.py` and the `alembic` configuration to the `api_service`.
    *   Create new models: `User`, `FormSchema`, `ApplicationFileLink`. Create new Alembic migrations.
*   **Task 2.2: Implement Application Endpoints.**
    *   Re-implement the logic for creating and retrieving applications. Focus on the core data logic first.
*   **Task 2.3: Implement Session & Auth Logic.**
    *   Create the session endpoints for Telegram (`/verify-user`, `/sessions/telegram`).
    *   The `MINI_APP_URL` should be retrieved from environment variables.
*   **Task 2.4: Implement DB-backed Form Schema.**
    *   Create the endpoints (`/forms/schema/active` and the admin CRUD endpoints) to serve the form schema from the `FormSchema` table.

### **Phase 3: Bot & File Service Implementation**
*   **Task 3.1: Rewrite Bot Service Logic.**
    *   Remove all FSM and form-processing logic from the old bot code.
    *   Implement the new logic: handle `/start`, call the `api-service` to create a session, and return the Mini App button.
    *   Implement the internal `/notify` endpoint.
*   **Task 3.2: Build the File Service.**
    *   Create the FastAPI app for the `file-storage-service`.
    *   Integrate the `boto3` (or equivalent) S3 client.
    *   Implement the `/files` upload endpoint that saves files to MinIO.
    *   Implement the `/files/{id}/download-link` endpoint that generates pre-signed URLs.

### **Phase 4: Finalizing Admin and Web Support**
*   **Task 4.1: Implement Admin Authentication.**
    *   Add OAuth 2.0 logic to the `api_service` for admin panel login.
*   **Task 4.2: Implement Web Widget Session Logic.**
    *   Add the "Magic Link" endpoints (`/sessions/web`) to the `api_service`.
    *   This will require integrating an email sending library/service.
*   **Task 4.3: Final Testing & Integration.**
    *   Perform end-to-end testing of all user flows: Telegram Mini App, Web Widget, and Admin Panel.