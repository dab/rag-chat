# Story 1.2: Enforce Max File Count

## Story

**As a** developer
**I want** to enforce a maximum of three uploaded files
**so that** users cannot exceed the limit.

## Status

Complete

## Context

Building on Story 1.1 where the file uploader was implemented, this story adds the specific constraint that no more than three files can be uploaded simultaneously. If the user attempts to upload more than three files, the application should prevent this or handle it gracefully, likely by displaying an informative error message (related to Story 1.4). This involves checking the count of files received from the `st.file_uploader` widget *before* proceeding with any further processing (like validation or storage).

## Estimation

Story Points: 1

## Acceptance Criteria

1. - [x] The application checks the number of files uploaded via the `st.file_uploader`.
2. - [x] If the number of uploaded files is greater than three, an error message is displayed to the user.
3. - [x] If the number of uploaded files is three or less, the application proceeds (or, for now, continues to show the success message from Story 1.1).
4. - [x] The error message clearly indicates that the maximum number of files allowed is three.

## Subtasks

1. - [x] Modify `app.py`
   1. - [x] Add a check for `len(uploaded_files)` after the `st.file_uploader` call.
   2. - [x] If `len(uploaded_files) > 3`, use `st.error()` to display a message like "You can only upload a maximum of 3 files at a time."
   3. - [x] Ensure the success message/file list from Story 1.1 only displays if the file count is valid (<= 3).

## Testing Requirements:**

    - Manual testing:
        - Try uploading 1, 2, and 3 files. Verify success message appears and no error.
        - Try uploading 4 or more files. Verify error message appears and success message does not.
    - (Unit tests can be added later when logic becomes more complex)

## Story Wrap Up (To be filled in AFTER agent execution):**

- **Agent Model Used:** `<Agent Model Name/Version>`
- **Agent Credit or Cost:** `<Cost/Credits Consumed>`
- **Date/Time Completed:** `<Timestamp>`
- **Commit Hash:** `<Git Commit Hash of resulting code>`
- **Change Log**
  - change X
  - change Y
    ... 