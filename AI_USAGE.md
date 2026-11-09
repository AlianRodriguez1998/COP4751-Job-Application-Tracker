# AI Usage Documentation — COP4751 Job Application Tracker

## Tools used

- **ChatGPT (OpenAI, GPT-6):** Helped generate the initial project files from the course specification, including the MySQL schema, Flask application, database helper, HTML/CSS interface, job-matching logic, tests, and README. It also provided step-by-step setup and troubleshooting guidance.
- **Visual Studio Code, MySQL Workbench, Git, and GitHub:** Used as development, database, version-control, and submission tools. These are not generative-AI tools.
- No other generative-AI tools are claimed in this record.

## Key prompts and AI-assisted tasks

The following reflects my actual conversation and the provided project requirements, rather than invented prompts:

1. **Project creation:** After uploading the official `Project_Specification.docx`, I replied **"yes please"** to ChatGPT's offer to build the Job Application Tracker using the professor's requirements. The requested deliverables included four related MySQL tables, complete CRUD, a dashboard, a skill-matching feature, HTML/CSS pages, automated tests, and repository documentation.
2. **Setup guidance:** I asked **"walk me through"** and followed ChatGPT's instructions for opening the project in VS Code, creating a Python virtual environment, installing dependencies, executing `schema.sql` in MySQL Workbench, configuring a local `.env` file, and starting Flask.
3. **Database and Flask integration:** ChatGPT explained how to connect the Flask app to MySQL, how to create the `job_tracker` schema, and how to verify records through both the web interface and SQL queries.
4. **Job matching and testing:** With ChatGPT's guidance, I tested the generated Job Match logic using `Python, SQL` against a job requiring `Python, SQL, Flask`. It correctly reported **67% (2/3 skills)** and identified **Flask** as missing.
5. **Troubleshooting and configuration:** I asked **"update it for me"** about the Flask secret-key placeholder. ChatGPT supplied a local PowerShell/Python command to generate and write a random secret into `.env`. I also followed its guidance to resolve PowerShell virtual-environment activation restrictions, install Git, configure my Git identity, and push the repository to GitHub.

## What worked well

- The generated application started with Flask and displayed a dashboard plus Companies, Jobs, Applications, Contacts, and Job Match pages.
- The four MySQL tables were created by running `schema.sql` in MySQL Workbench. The schema includes foreign keys and JSON columns for job requirements and interview data.
- Creating and reading sample companies, jobs, applications, and contacts worked in the browser. Dashboard counts updated as records were added.
- All four basic CRUD operations were manually tested for each of the four entities, including edit confirmations and delete confirmations.
- The Job Match page showed the expected 67% partial match and the missing skill.
- The Python automated test suite finished with **9 tests passing**.
- GitHub accepted the initial commit and the project was pushed to the `main` branch.

## Modifications, integration, and corrections I performed

These are the changes and setup decisions I actually made; they should not be confused with independently rewriting the generated application logic.

- **Local database configuration:** I copied `.env.example` to `.env` and configured the connection settings for my local MySQL instance, including the `job_tracker` database. I kept `.env` out of version control.
- **Python environment:** I created a `.venv` environment. Because PowerShell blocked its activation script, I installed dependencies directly with `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` rather than changing machine-wide security policy.
- **Database initialization:** I executed the provided `schema.sql` in MySQL Workbench and checked that the creation commands succeeded.
- **Application testing:** I added a sample company and related job, application, and contact. I edited records and removed them after verifying the Create, Read, Update, and Delete actions.
- **Configuration security:** I generated a local Flask secret key and checked that `.gitignore` excludes `.env` and `.venv/`. No credentials or secret values are included in this document.
- **Git/GitHub setup:** I installed Git, set my commit identity, initialized the repository, checked the ignored files, committed the project, and pushed to the public GitHub repository.

**Application code edits:** I have not documented independent source-code modifications to the AI-generated Flask routes, SQL queries, templates, or matching algorithm. If I make such changes before submission, I will add each one here with the reason and a corresponding Git commit.

## What I learned

- A Flask web page can interact with MySQL only when the database schema exists and the application's local connection settings are correct.
- Foreign keys connect jobs to companies, applications to jobs, and contacts to companies. Creating related records in that order makes the relationships easier to test.
- MySQL JSON columns can store skill requirements as arrays, such as `["Python", "SQL", "Flask"]`, instead of only unstructured text.
- For skill matching, the percentage can be calculated as `(matched required skills / total required skills) * 100`. Matching two out of three skills gives approximately 67%; missing skills should be shown rather than treated as matches.
- Automated tests and hands-on browser testing catch different kinds of issues. Passing tests is useful, but I also need to check forms, database behavior, and the final setup instructions.
- AI-generated code and instructions still require local configuration, careful testing, and accurate attribution. I should not claim changes or tests that I did not perform.
- Git's `.gitignore` protects locally configured files from accidental staging when it is set correctly. I verified ignored-file behavior before the first upload.

## Testing and verification performed

**Date: November 9, 2026**

- **Automated tests:** Ran `\.venv\Scripts\python.exe -m unittest discover -s tests -v` in VS Code. Result: **9 tests ran; OK**.
- **Flask startup:** Ran `\.venv\Scripts\python.exe app.py` and opened the local site at `http://127.0.0.1:5000`.
- **Companies CRUD:** Created, viewed, edited, and deleted a test company.
- **Jobs CRUD:** Created, viewed, edited, and deleted a test job linked to that company.
- **Applications CRUD:** Created, viewed, updated the status of, and deleted a test application linked to the job.
- **Contacts CRUD:** Created, viewed, edited, and deleted a test contact linked to the company.
- **Job Match:** Entered `Python, SQL` for a role requiring `Python, SQL, Flask`; the app displayed **67% (2/3)** with **Flask missing**.
- **MySQL verification:** Executed `SELECT COUNT(*)` queries against the four tables after deleting test records. Workbench reported successful execution; the visible Contacts result was `0`. The other result tabs can be checked separately if needed.
- **GitHub:** Uploaded the repository on the `main` branch and confirmed that the source files, templates, tests, README, and this documentation appear in the public repository, while `.env` is excluded.

### Still to complete before submission

- Rehearse setup from a **fresh clone** using only `README.md`, `requirements.txt`, and `schema.sql`; record the result here.
- Record and upload the professor's mandatory **3–7 minute demonstration video** showing the browser, Flask server, and MySQL database; add the exact video filename here after upload.
- Revisit validation and foreign-key edge cases, if time allows, and record any additional test outcomes or code changes accurately.

## Responsibility statement

I used ChatGPT to assist with initial implementation, setup, and troubleshooting. I am responsible for understanding the submitted project, verifying that it runs, documenting my actual actions, and clearly distinguishing AI-generated files from my own configuration and testing work.
