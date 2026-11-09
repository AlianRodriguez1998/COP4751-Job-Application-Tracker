# AI Usage Documentation — COP4751 Job Application Tracker

> This file records a starting point for AI-assisted development. Update it with **your actual prompts, edits, test results, and decisions** before submitting. Do not claim unperformed work.

## Tools used

- **ChatGPT (OpenAI, GPT-6)** — initial scaffold for the MySQL schema, Flask backend, HTML/CSS pages, skill-matching function, test suite, and setup documentation.
- Other tools (only if personally used): _add here_.

## Key prompts and tasks

1. **User request:** "yes please" in response to the proposal to build the COP4751 Job Application Tracker from the uploaded official Project Specification. The supplied requirements described four MySQL tables, Flask/Python, HTML/CSS, CRUD, dashboard, skill matching, and GitHub deliverables.
2. **AI-assisted implementation tasks:** Create the schema and relationship constraints; implement parameterized database helpers and CRUD routes; validate required fields and JSON; calculate skill-match percentage; create responsive templates; write the README and baseline tests.
3. **Additional prompts you personally issue:** _record the exact prompt text and date here_.

## What worked well

- The initial code organizes the four required entities in a single schema and uses a configurable connection helper.
- The matching feature is isolated in `matching.py` so the ranking logic can be unit-tested without MySQL.
- The starter README describes how to recreate the MySQL schema from a fresh clone.

## Modifications and corrections made by the student

_To complete after you inspect and run the application. Examples of things you could investigate (do not claim these unless actually done):_

- [ ] Adjust field labels, colors, layout, or navigation based on your testing.
- [ ] Add or update validation for an edge case you discovered.
- [ ] Fix a bug encountered while testing against your local MySQL installation.
- [ ] Improve or clarify the README after following it on your own computer.

For each actual change, note **what was generated**, **what you changed**, and **why**.

## What I learned

_Complete in your own words after running the project. Suggested reflection topics:_

- Why parameterized SQL prevents values from being inserted directly into query strings.
- How MySQL foreign keys preserve referential integrity and JSON fields store structured data.
- Why missing job requirements should not be counted as a perfect skill match.
- Why AI-generated code still needs manual review, testing, and adaptation.

## Testing and verification performed

- **Automated local tests:** _record the date, command, and actual results after running_.
- **MySQL end-to-end tests:** _record what you verified in Workbench and the browser_.
- **Fresh clone rehearsal:** _record the date and outcome_.
- **Demo recording:** _record the date and uploaded filename_.

## Responsibility statement

I am responsible for reviewing, understanding, modifying, and testing AI-assisted output. All statements above should accurately reflect my actual workflow before submission.
