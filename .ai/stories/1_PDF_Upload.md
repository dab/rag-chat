# Epic 1: PDF Upload

Story 1.1: As a user, I want to upload up to three PDF files (<50 MB each) via a Streamlit file uploader so that the system can process my documents.
Story 1.2: As a developer, I want to enforce a maximum of three uploaded files so that users cannot exceed the limit.
Story 1.3: As a developer, I want to validate uploaded files to ensure only PDF file types and size <50 MB are accepted so that invalid uploads are rejected.
Story 1.4: As a user, I want to see clear error notifications for invalid uploads (e.g., "Only PDFs allowed" or "File too large") so that I understand why an upload failed.
Story 1.5: As a system, I want to store validated PDFs temporarily in memory or session storage so that they are available for RAG processing. 