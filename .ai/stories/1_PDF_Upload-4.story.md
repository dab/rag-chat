# Story 1.4: Clear Error Notifications

## Story

**As a** user
**I want** to see clear error notifications for invalid uploads (e.g., "Only PDFs allowed" or "File too large")
**so that** I understand why an upload failed.

## Status

Complete

## Context

This story ensures that users receive immediate and understandable feedback when an upload fails due to exceeding the file count limit, incorrect file type, or excessive file size. The specific error messages (`st.error`) for these conditions were implemented as part of Story 1.2 (max count check) and Story 1.3 (type and size validation). This story primarily serves as a confirmation that these error messages are clear and meet the user's need for feedback.

## Estimation

Story Points: 0 (Covered by previous stories)

## Acceptance Criteria

1. - [x] If more than 3 files are uploaded, a clear error message stating the limit is displayed (Implemented in Story 1.2).
2. - [x] If a non-PDF file is uploaded, a clear error message stating only PDFs are allowed (or similar) is displayed for that file (Implemented in Story 1.3).
3. - [x] If a file exceeding 50MB is uploaded, a clear error message stating the size limit is displayed for that file (Implemented in Story 1.3).
4. - [x] Error messages identify the specific file causing the issue where applicable (type/size errors) (Implemented in Story 1.3).

## Subtasks

1. - [x] Review existing error messages in `app.py` implemented in Stories 1.2 and 1.3.
   1. - [x] Confirm error for max files (`len(uploaded_files) > MAX_FILES`).
   2. - [x] Confirm error for invalid type (`file.type not in ALLOWED_MIME_TYPES`).
   3. - [x] Confirm error for invalid size (`file.size > MAX_FILE_SIZE_BYTES`).
2. - [-] (No code changes anticipated unless review identifies need for clarification in messages).

## Testing Requirements:**

    - Manual Testing (Performed as part of Story 1.2 and 1.3 testing):
        - Verify specific error messages appear correctly for exceeding count, wrong type, and exceeding size.

## Story Wrap Up (To be filled in AFTER agent execution):**

- **Agent Model Used:** `<Agent Model Name/Version>`
- **Agent Credit or Cost:** `<Cost/Credits Consumed>`
- **Date/Time Completed:** `<Timestamp>`
- **Commit Hash:** `<Git Commit Hash of resulting code>`
- **Change Log**
  - (Likely no changes)
    ... 