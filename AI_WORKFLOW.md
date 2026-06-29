# AI Workflow — Weather Recorder

This document describes how Claude Code (Anthropic's CLI) was used to build this project, including specific prompts, workflows, and what was reviewed manually.

---

## Tool Used

**Claude Code** — Anthropic's CLI that runs Claude directly in the terminal alongside the codebase. It can read files, write code, run shell commands, and maintain context across a session.

---

## How the Project Was Structured for AI Collaboration

Before writing any code, a `CLAUDE.md` file was created in the project root. This acts as a persistent instruction set that Claude Code reads at the start of every session. It defined:

- The project goal and stack
- The exact database schema to use
- The API endpoints and their expected behavior
- Error handling requirements (which HTTP status codes map to which conditions)
- A working discipline: one feature at a time, verify syntax after every file, update progress docs after every feature

This approach meant Claude Code had a consistent, unambiguous specification to work from — reducing hallucination and keeping every session on track regardless of context drift.

---

## Session Workflow

Each development session followed this loop:

```
1. Claude reads docs/claude-progress.md  → understands current state
2. Claude reads docs/feature_list.json   → picks highest priority not_started feature
3. Claude writes the code
4. Claude verifies syntax: python -m py_compile <file>
5. Claude runs a live test where possible
6. Claude updates feature_list.json status to "passing"
7. Claude writes a session entry in claude-progress.md
8. Claude commits with a structured commit message
```

This created a clean, auditable trail — each commit maps to one feature, and the progress docs reflect exactly what was tested and how.

---

## Specific Prompts and Workflows

### Project scaffolding
> *"Go through the CLAUDE.md and project files to get a glimpse"*

Claude read all existing files, identified the current state, and proposed the feature build order. No code was written until the full picture was understood.

### Security incident response
> *"1 internal secret incident detected — Generic Password"*

GitGuardian flagged credentials committed to a public repo. The prompt to Claude was simply to fix it. Claude audited every file, identified three sources of leaked credentials (`docs/deploy.md`, `docs/feature_list.json`, `.env.example`), scrubbed them, deleted the local `.git` history, reinitialised the repo clean, and pushed a fresh initial commit — without being told the step-by-step fix.

### Feature development pattern
> *"go ahead with db-init"* / *"go ahead with weather-fetch"* / etc.

Each feature was triggered with a short natural-language prompt. Claude inferred the full implementation from `CLAUDE.md` and the feature spec in `feature_list.json`, wrote the code, ran verification, and committed — all in one turn.

### Reliability review
> *"do you think our system is reliable — think and validate every test case possible to you"*

Claude performed a systematic audit across input edge cases, infrastructure failure modes, and security surface. This surfaced an XSS vulnerability in the history table (`innerHTML` with unsanitised API data) and a server crash path (non-JSON API response not caught as `WeatherAPIError`). Both were fixed immediately and committed.

### Architectural discussion
> *"did we follow any type of structure — atomic, MVC, MVVM?"*

Rather than retrofitting a pattern, Claude explained the natural layered separation that emerged (`db.py` → data, `weather.py` → external service, `main.py` → API, `index.html` → presentation) and confirmed it was appropriate for the project scope without over-engineering.

---

## What Was Reviewed Manually

AI-generated code was not merged blindly. The following were reviewed by hand before each commit:

- **SQL queries** — upsert logic, JOIN correctness, parameterized query syntax
- **Error mapping** — verifying each exception type maps to the right HTTP status code
- **Commit messages** — reviewed and occasionally revised before pushing (e.g., removed a note about credential scrubbing that would have been unprofessional in a public commit history)
- **Security decisions** — the XSS fix and the credential removal process were both human-initiated concerns that Claude then executed
- **Live test output** — every `curl` response and browser screenshot was read and validated before marking a feature passing

---

## What Claude Code Did Not Do

- Claude did not create the GitHub repository (browser action)
- Claude did not SSH into the droplet autonomously — all server-side commands were run by the developer after review
- Claude did not make architectural decisions unilaterally — each feature was approved before implementation began

---

## Summary

Claude Code acted as a senior pair programmer that held the full project spec in memory, enforced discipline (one feature at a time, always verify, always document), and caught issues (security, reliability) that might have slipped through under time pressure. The human role was direction, review, and final approval at each step.
