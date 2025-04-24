# Story 1.3: Validate PDF Type and Size

## Story

**As a** developer
**I want** to validate uploaded files to ensure only PDF file types and size <50 MB are accepted
**so that** invalid uploads are rejected.

## Status

Complete

## Context

Following Story 1.1 (upload) and 1.2 (count limit), this story focuses on validating the *individual* files that pass the initial count check. Each uploaded file (up to 3) must be checked to ensure it is a PDF (`type == 'application/pdf'`) and its size does not exceed 50 MB. Files failing validation should trigger appropriate error messages (covered further in Story 1.4). Validated files will eventually be stored (Story 1.5).

## Estimation

Story Points: 1

## Acceptance Criteria

1.  - [x] For each uploaded file (within the 3-file limit), its type is checked.
2.  - [x] If a file's type is not 'application/pdf', an error message is displayed for that specific file.
3.  - [x] For each uploaded file, its size is checked.
4.  - [x] If a file's size exceeds 50 MB (50 * 1024 * 1024 bytes), an error message is displayed for that specific file.
5.  - [x] Files that pass both type and size validation are identified separately from invalid files.
6.  - [x] The success message should only list valid files (or indicate if all are invalid).

## Subtasks

1. - [x] Define Constants
   1. - [x] Add `MAX_FILE_SIZE_MB = 50` to `app.py`.
   2. - [x] Add `ALLOWED_TYPES = ['application/pdf']` to `app.py`.
2. - [x] Modify `app.py` validation logic
   1. - [x] Inside the `else` block (where file count <= 3), iterate through `uploaded_files`.
   2. - [x] For each `file`, check `file.type` against `ALLOWED_TYPES`.
   3. - [x] For each `file`, check `file.size` against `MAX_FILE_SIZE_MB * 1024 * 1024`.
   4. - [x] Keep track of valid files and invalid files (and reasons for invalidity).
   5. - [x] Display errors using `st.error()` for each invalid file, mentioning the filename and reason (e.g., "{file.name} is not a PDF." or "{file.name} exceeds 50MB limit.").
   6. - [x] Modify the `st.success()` message to only list the names of *valid* files. If no files are valid, display an appropriate message (e.g., "No valid PDF files were uploaded.").

## Testing Requirements:**

    - Manual testing:
        - Upload valid PDFs (<50MB). Verify success message lists them.
        - Upload a non-PDF file (e.g., .txt, .jpg). Verify error message for that file and it's not listed in success.
        - Upload a PDF larger than 50MB. Verify error message for that file and it's not listed in success.
        - Upload a mix of valid and invalid files. Verify errors for invalid ones and success lists only valid ones.
        - Upload only invalid files. Verify errors and no success message (or a 'no valid files' message).

## Story Wrap Up (To be filled in AFTER agent execution):**

- **Agent Model Used:** `<Agent Model Name/Version>`
- **Agent Credit or Cost:** `<Cost/Credits Consumed>`
- **Date/Time Completed:** `<Timestamp>`
- **Commit Hash:** `<Git Commit Hash of resulting code>`
- **Change Log**
  - change X
  - change Y
    ... 