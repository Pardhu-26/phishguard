# PhishGuard v2 — Project Report

---

## Project Title

**PhishGuard: An Educational Email Phishing Awareness Tool**

---

## Project Overview

PhishGuard (v2) is a beginner-friendly web application built with Python and Streamlit. It helps people learn to recognise common phishing clues by analysing email text or an uploaded `.eml` file. The app walks the user through three clear stages — providing an email, reviewing findings, and reading educational context — organised as separate tabs.

Analysis uses transparent keyword-and-pattern rules (no machine learning, no external APIs). Every finding explains *what* was detected, *why* it matters, and *what safe action the user can take*. A downloadable Markdown report summarises the findings. A rotating tip appears once per session to keep awareness advice varied.

PhishGuard is an **educational learning aid, not a security product**. A Low risk score does **not** mean an email is safe.

---

## Problem Statement

Phishing remains one of the most effective and common social-engineering attacks. Many people — especially those new to cybersecurity — do not know what to look for in a suspicious email. Professional email security tools exist but are typically inaccessible to learners: they operate invisibly, give no educational feedback, and require infrastructure the average beginner does not have.

There is a gap between reading a tip sheet about phishing and actually practising recognition skills. PhishGuard fills that gap with an interactive, explainable tool that shows *which* clues triggered an alert and *why* each one is suspicious — making learning active rather than passive.

---

## Objectives

1. Let users provide an email by uploading a `.eml` file or pasting text directly.
2. Parse `.eml` files using Python's standard-library `email` package and extract useful headers (From, Reply-To, Subject) and the body.
3. Run transparent keyword-and-pattern checks and present findings with plain-English explanations, including what was detected, why it matters, and a safe action.
4. Detect and report a From / Reply-To domain mismatch when both are present.
5. List URLs found in the email as plain text only — never fetch, visit, or render them.
6. Report attachment filenames found in `.eml` files and advise the user accordingly.
7. Show a risk estimate (Low, Medium, High) with a clear visual treatment.
8. Provide a downloadable plain-text/Markdown report of the findings.
9. Show one randomly chosen phishing-awareness tip per session, kept stable during the session.
10. Organise the experience into focused tabs so the interface is not a single long form.
11. Ensure no email content is saved, logged, or transmitted beyond the current session.

---

## Target Users

- Cybersecurity bootcamp students and beginners.
- Employees completing basic security-awareness training.
- General internet users who want to strengthen their phishing recognition skills.
- Educators looking for a classroom demonstration tool.

---

## Features

| Feature | Description |
|---|---|
| **Tab layout** | Three tabs: *Provide Email*, *Review Findings*, and *Learn More* — replacing a single long page. |
| **`.eml` file upload** | Users can upload a real `.eml` file (max 200 KB). The app parses headers and body using Python's standard `email` library. |
| **Paste email text** | Users can type or paste a plain-text email body directly. Optional From, Reply-To, and Subject fields enable richer checks. |
| **Conflict resolution** | If both a file and pasted text are provided, the user is asked to choose which to analyse. |
| **HTML email handling** | If an uploaded email has only an HTML body, the app converts it to plain text safely (no live rendering) and notes the limitation. |
| **10 pattern-based clue checks** | Checks for urgent language, password requests, financial requests, personal info requests, URLs, IP-address links, shorteners/lookalike domains, generic greetings, attachment mentions, and authority impersonation. |
| **Actual attachment detection** | Attachment filenames from `.eml` files are listed and flagged; risky extensions score higher. |
| **Sender / Reply-To mismatch** | Flags when the From and Reply-To addresses belong to different domains. |
| **URL listing** | All URLs found in the email are displayed as plain code blocks — never as clickable links. |
| **Risk card** | Colour-coded card (🟢 Low / 🟡 Medium / 🔴 High) with score and progress bar. |
| **Structured findings** | Each finding shows: what was detected, why it may matter, and a safe action to take. |
| **Recommended next steps** | Risk-level-appropriate actions listed below the findings. |
| **Downloadable report** | A Markdown report containing the risk estimate and findings (email body excluded by default). |
| **Rotating session tip** | One randomly selected phishing-awareness tip, stable for the whole session. |
| **Learn More tab** | Expandable sections covering what phishing is, how the scoring works, clue categories, limitations, and recommended actions. |
| **Four fictional demo samples** | Low, Medium, and two High-risk fictional sample emails to demonstrate the tool safely. |
| **Privacy notice** | Prominent expandable banner advising users not to upload real confidential emails. |

---

## Tools and Technologies

| Tool / Technology | Role |
|---|---|
| **Python 3.10+** | Core programming language |
| **Streamlit ≥ 1.32** | Web application framework — UI, tabs, session state, file upload, download button |
| **`email` + `email.policy`** (stdlib) | Parsing `.eml` files and extracting MIME parts |
| **`re`** (stdlib) | Regular-expression pattern matching for phishing clue detection |
| **`html`** (stdlib) | Safely converting HTML entity codes to plain text |
| **`random`** (stdlib) | Selecting the rotating tip at session start |
| **`datetime`** (stdlib) | Timestamping the downloaded analysis report |
| **`textwrap`** (stdlib) | Imported for potential text formatting (used in report building) |
| No external APIs | All logic runs locally; no network calls are made |
| No machine learning | All rules are explicit, readable, and beginner-understandable |

---

## How Email Analysis Works

### Input handling

- **`.eml` upload:** The file is read as raw bytes, validated against a 200 KB size limit, then parsed with `email.message_from_bytes()` using `policy.default` for clean Unicode output. The parser walks all MIME parts, collects the plain-text body (falling back to a stripped version of the HTML body if no plain text is present), records attachment filenames, and extracts From, Reply-To, and Subject headers.
- **Pasted text:** The body text is used directly. Header fields (From, Reply-To, Subject) are optional and entered separately.

### Analysis engine (`analyze_email_content`)

The `analyze_email_content()` function accepts the body, header strings, and attachment list. It concatenates the From address, Reply-To address, and body into a single searchable string, then runs every pattern in `CLUE_DEFINITIONS` as a case-insensitive `re.search()`. Each match adds its points to a running total. Actual attachment filenames from `.eml` files are checked separately; risky extensions (`.exe`, `.zip`, `.docm`, `.xlsm`, `.js`, `.bat`, `.vbs`) score 30 points, others score 15.

The total score is capped at 100 and mapped to a risk level:

```
0–24   → 🟢 Low Risk
25–54  → 🟡 Medium Risk
55–100 → 🔴 High Risk
```

### The 10 clue categories checked by pattern

| # | Clue | Points |
|---|---|---|
| 1 | Urgent or threatening language | 25 |
| 2 | Request for password or PIN | 30 |
| 3 | Request for payment or financial details | 30 |
| 4 | Request for sensitive personal information | 25 |
| 5 | Links present in the email | 10 |
| 6 | Link using a raw IP address | 35 |
| 7 | URL shortener or lookalike domain | 35 |
| 8 | Generic, impersonal greeting | 15 |
| 9 | Unexpected attachment mentioned or present | 20 |
| 10 | Impersonation of IT, security, bank, or delivery service | 20 |

### Sender / Reply-To mismatch check

The `check_sender_reply_to_mismatch()` function extracts the domain after `@` in both the From and Reply-To headers. If both are present and the domains differ, a separate warning is displayed. This is a common trick to ensure replies go to the attacker rather than the spoofed sender.

### URL listing

All URLs in the email body are extracted with `re.findall()` and displayed as plain `st.code()` blocks — never as clickable hyperlinks — so the user can read them without accidentally visiting them.

---

## Privacy and Safety

- **No email content is stored, logged, or transmitted.** Uploaded bytes and pasted text exist only in the Streamlit server process for the current session and are discarded when the session ends.
- **Uploaded HTML is never rendered as active page content.** The `extract_text_from_html()` function strips all tags and decodes entities; the result is treated as plain text only.
- **Attachments are never opened, executed, or scanned.** Only filenames are recorded and reported to the user.
- **URLs are listed as plain text only.** PhishGuard makes no network requests and does not fetch, visit, or preview any link.
- **A privacy notice** is shown prominently at the top of the app. It explicitly advises users not to upload real confidential emails and to close the browser tab on shared computers.
- **The downloadable report** excludes the full email body by default. A caption warns users that the report may still contain subject lines or domain names if those appeared in the findings.
- The app contains **no real phishing links, real credentials, or instructions for carrying out phishing**.

---

## Testing Performed

The following are **suggested manual test cases** that a beginner can run to verify the app behaves as expected. These are recommended tests, not automated test results that were executed as part of this project.

### Test 1 — Empty input
**Steps:** Open the app, leave all inputs blank, click Analyse.  
**Expected:** An info message prompts the user to provide input. No crash.

### Test 2 — Low-risk fictional sample (pasted text)
**Steps:** On the *Provide Email* tab, select "🟢 Low Risk — Monthly newsletter (fictional)" from the dropdown. Click Analyse.  
**Expected:** 🟢 Low Risk, score below 25, only the "Links present" clue (or none) triggered.

### Test 3 — High-risk fictional sample (pasted text with headers)
**Steps:** Select "🔴 High Risk — Account suspension scam (fictional)". Observe that From, Reply-To, and Subject fields are pre-filled. Click Analyse.  
**Expected:** 🔴 High Risk, score ≥ 55. Clues should include urgent language, password request, payment request, IP-address link, and generic greeting. No sender/Reply-To mismatch (both addresses share the same domain in this sample).

### Test 4 — Medium-risk sample with Reply-To mismatch
**Steps:** Select "🟡 Medium Risk — Prize notification (fictional)". The From and Reply-To fields show different domains. Click Analyse.  
**Expected:** 🟡 Medium Risk. A separate mismatch warning is shown above the findings.

### Test 5 — Fake parcel delivery sample
**Steps:** Select "🔴 High Risk — Fake parcel delivery (fictional)". Click Analyse.  
**Expected:** 🔴 High Risk. Clues should include a URL shortener (bit.ly), urgent language, payment request, and authority impersonation (delivery service).

### Test 6 — Conflict handling
**Steps:** Upload any `.eml` file AND paste some text into the text area. Click Analyse.  
**Expected:** A warning appears asking the user to choose which input to analyse; a radio button is shown.

### Test 7 — Oversized file
**Steps:** Attempt to upload a `.eml` file larger than 200 KB.  
**Expected:** An error message explains the size limit. No crash.

### Test 8 — Download report
**Steps:** After completing any analysis, go to the *Review Findings* tab and click "Download report (.md)".  
**Expected:** A Markdown file (`phishguard_report.md`) is downloaded containing the risk level, score, and findings. The email body is not included.

### Test 9 — Learn More tab
**Steps:** Open the *Learn More* tab and expand each section.  
**Expected:** All expandable sections open correctly and display their content.

### Test 10 — Rotating tip stability
**Steps:** Run the analysis or click other buttons multiple times.  
**Expected:** The tip at the top of the page does not change during the session.

---

## Limitations

- **Simple pattern matching is not foolproof.** A sophisticated phishing email that avoids the checked keywords will score Low. A Low score does **not** mean an email is safe.
- **No URL fetching or DNS lookup.** PhishGuard cannot visit links or check where they lead; it only inspects the URL text itself.
- **English only.** All patterns are written for English-language emails.
- **No cryptographic header verification.** The app cannot check SPF, DKIM, or DMARC records, which are required to detect email spoofing reliably.
- **No attachment scanning.** Attached files are never opened, executed, or scanned for malware.
- **False positives are possible.** Legitimate emails — a real password reset, a bank statement, an IT support email — may trigger clues.
- **No persistence.** All analysis results and session data are lost when the browser tab is closed.
- **`.eml` files only.** The upload accepts only `.eml` format. Other formats (`.msg`, raw MBOX) are not supported.
- **HTML-only emails are analysed with reduced accuracy.** The HTML-to-text conversion strips some content that may be relevant.

---

## Future Improvements

- **Header deep-dive:** Parse and display Received headers, X-Originating-IP, and DKIM signature status.
- **Broader lookalike domain detection:** Use edit-distance heuristics to detect domains similar to a configurable list of trusted brands rather than relying on a hard-coded list.
- **Multi-language support:** Extend pattern sets for phishing in languages other than English.
- **Larger sample library:** Add more fictional, sanitised examples covering spear-phishing, CEO fraud, and invoice-redirect scams.
- **Session history:** Show a list of analyses run in the current session so the user can compare results.
- **Accessibility:** Improve screen-reader labels, keyboard navigation, and high-contrast mode support.
- **`.msg` support:** Accept Outlook `.msg` files in addition to `.eml`.
- **Configurable scoring:** Let users adjust the weight of each clue category to explore how the score changes.

---

## Conclusion

PhishGuard v2 demonstrates how Python's standard library and Streamlit can be combined into a practical, transparent educational security tool. The redesign replaced a single long page and a quiz with a focused three-tab flow: provide an email, review findings, and learn more. Key improvements over v1 include `.eml` file parsing, structured three-part findings (what / why / action), sender/Reply-To mismatch detection, URL listing as plain text, attachment filename reporting, a downloadable Markdown report, and a rotating session tip.

The project covers core Python concepts — functions, regular expressions, dictionaries, MIME parsing, and Streamlit's session state and component model — while remaining readable enough for a beginner to understand, modify, and extend. Most importantly, it is honest about what it can and cannot do: every finding explains its reasoning, and the app consistently reminds users that its results are educational indicators, not security verdicts.

---

*Report prepared as part of a cybersecurity portfolio project. All sample emails used in the application are entirely fictional and were created for educational purposes only.*
