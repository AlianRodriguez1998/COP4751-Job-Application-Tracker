# Job Application Tracker (COP4751)

A full-stack application for tracking companies, job listings, applications, contacts, and skill-based job matches. Built with MySQL, Python 3, Flask, HTML, and CSS.

## Features

- Dashboard with totals, recent applications, and a status pipeline.
- Complete CRUD for **companies, jobs, applications, and contacts**, including list and detail views, validation, and delete confirmations.
- MySQL foreign keys and JSON columns (`jobs.requirements`, `applications.interview_data`).
- Job Match: enter comma-separated skills to rank jobs by percentage of required skills matched, displaying matched and missing skills.
- Responsive interface and parameterized SQL queries.

## Prerequisites

- Python 3.10 or later
- MySQL Server 8.0 or later (running locally)
- Git (for cloning)

## Install and run from a fresh clone

1. Clone and open the repository:

   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   cd YOUR-REPOSITORY
   ```

   Replace the example URL and folder name with the actual repository location.

2. Create and activate a virtual environment:

   **Windows PowerShell:**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create the database. Start MySQL, then run from the project directory:

   ```bash
   mysql -u root -p < schema.sql
   ```

   If that command is unavailable on Windows, open **MySQL Workbench**, select **File → Open SQL Script**, select `schema.sql`, and run the script. Tables are initially empty; add records through the app.

5. Copy `.env.example` to `.env` and edit the credentials for your local MySQL installation (do not commit `.env`):

   **Windows PowerShell:** `Copy-Item .env.example .env`

   **macOS / Linux:** `cp .env.example .env`

   Set `DB_USER`, `DB_PASSWORD`, and any non-default host, port or database name. Generate a long random string for `FLASK_SECRET_KEY`. Example generator:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

6. Run the server:

   ```bash
   python app.py
   ```

7. Open **http://127.0.0.1:5000** in a browser. Start with **Companies → Jobs → Applications**; Contacts can be added after Companies.

## Database relations

- `companies (1) → (many) jobs`
- `companies (1) → (many) contacts`
- `jobs (1) → (many) applications`

Foreign keys use **RESTRICT** on deletion to avoid accidental data loss. Delete child records first when deleting a parent.

## Job Match calculation

Store required skills as a comma-separated list in the Job form. They are persisted as a JSON array, e.g. `["Python", "SQL", "Flask"]`.

Enter your skills in **Job Match**, e.g. `Python, SQL, Flask`.

```
match_percent = round(100 × number_of_required_skills_matched / number_of_required_skills)
```

Matching ignores capitalization and whitespace, removes duplicate skills, and orders jobs highest percentage first. Example: if a job requires Python, SQL and Tableau and you enter Python, SQL, Flask, you match **2 of 3 (67%)**, missing Tableau. A job with no required skills is shown as **Not rated** rather than misleadingly 0% or 100%.

## Tests

The project includes dependency-free `unittest` checks for the algorithm, validation, and Flask page rendering with mock database responses:

```bash
python -m unittest discover -s tests -v
```

### Manual end-to-end checklist (real MySQL)

1. Add a company and confirm it is listed and has a detail page.
2. Edit its city; refresh and confirm the changed value.
3. Add a job linked to the company with `Python, SQL, Tableau` requirements; check `jobs.requirements` is JSON in MySQL Workbench.
4. Create an application linked to the job with a date, status, and sample interview JSON (`{"round": 1}`).
5. Add a contact linked to the company.
6. Confirm Dashboard totals and pipeline update.
7. In Job Match, enter `Python, SQL, Flask`; confirm **67% (2/3)** and missing **Tableau**.
8. Edit/delete a contact and confirm the changes; test CRUD for each other entity.
9. Attempt deleting a company that still has jobs; verify the error message explains related records.
10. Verify delete confirmation, validation for empty required fields, invalid JSON, and invalid salary range.
11. Repeat the setup from a fresh repository clone to confirm all instructions work.

## Submission video (required)

Record a **3–7 minute video** and upload the **video file itself** to this repository before submitting (not merely an external link). Show:

- MySQL tables and relationships/data in MySQL Workbench.
- The Flask server running in a terminal.
- The browser: dashboard, creating/editing/deleting a record for each entity, and Job Match results.
- A quick mention of README and AI_USAGE.md.

**Important:** This repository contains source code and a demo checklist, not a recorded video. A real recording of your locally running app must be added to meet the professor's grading requirement. Check GitHub's file upload size limit; if necessary use Git LFS, and ensure the instructor can retrieve and play the actual file. Never include database passwords in the recording.

## Project files

- `app.py`: Flask routes and validation
- `database.py`: MySQL connection and query helpers
- `matching.py`: skills ranking logic
- `schema.sql`: complete MySQL schema
- `templates/`: HTML templates
- `static/style.css`: CSS
- `AI_USAGE.md`: AI-assisted development documentation template
- `tests/`: automated tests
- `.env.example`: example configuration (real `.env` is ignored)

## Troubleshooting

- **Access denied:** Verify `.env` credentials match a MySQL user with access to `job_tracker`.
- **Unknown database/table:** Run `schema.sql` in MySQL Workbench or the `mysql` CLI.
- **Cannot connect:** Start MySQL and verify `DB_HOST`/`DB_PORT`.
- **Foreign key error on deletion:** Remove dependent records before deleting a company or job.
- **Port 5000 busy:** Stop the other process, or launch with `flask --app app run --port 5001` and open the new port.

This is a local demonstration project. It does not provide user authentication or multi-user data separation and should not be deployed publicly with real personal applicant data without additional security work.
