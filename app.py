# =============================================================================
# PhishGuard — Educational Phishing Awareness Tool  (v2)
# Built with Python and Streamlit
# =============================================================================
# PURPOSE   : Help beginners learn to spot common phishing clues in emails.
# IMPORTANT : This is a LEARNING AID, not a security product.
#             A low risk score does NOT mean an email is safe.
# =============================================================================

import email          # standard-library: parse .eml files
import html           # standard-library: safely convert HTML entities to text
import random         # standard-library: pick a random tip on each new session
import re             # standard-library: pattern matching
from datetime import datetime  # standard-library: timestamp on exported report
from email import policy       # standard-library: modern email parsing policy

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION  (must be the first Streamlit call in the script)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PhishGuard — Phishing Awareness",
    page_icon="🛡️",
    layout="wide",            # wide gives us room for a proper dashboard layout
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE-WIDE CSS  — PhishGuard dashboard theme
#
# Philosophy:
#   • Base colours & font come from .streamlit/config.toml (no duplication).
#   • This block adds: page background gradient, custom card classes, syntax
#     for email addresses / URLs (monospace), and decorative details that
#     Streamlit's theme tokens cannot express.
#   • All selectors use stable class names we inject ourselves — we avoid
#     fragile generated Streamlit class names.
#   • Contrast ratios are WCAG AA against their backgrounds.
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ═══════════════════════════════════════════════════════════════════════
       1. GLOBAL CANVAS
       Subtle radial gradient so the background has depth without distracting.
       The faint dot-grid reinforces the "tech / security" aesthetic while
       staying completely invisible in expanders and widget backgrounds.
    ═══════════════════════════════════════════════════════════════════════ */
    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 20% 10%, #0d2a3a 0%, transparent 55%),
            radial-gradient(ellipse at 80% 80%, #0a1f30 0%, transparent 50%),
            #0b0f19;
    }

    /* Faint circuit-dot grid overlay — pure CSS, no external assets */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image:
            radial-gradient(circle, rgba(0,212,200,0.06) 1px, transparent 1px);
        background-size: 32px 32px;
        z-index: 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       2. CONTENT COLUMN
       Centre the content and cap its width so it reads well on any laptop.
    ═══════════════════════════════════════════════════════════════════════ */
    .block-container {
        max-width: 960px !important;
        padding: 2.5rem 2rem 4rem 2rem !important;
        position: relative;
        z-index: 1;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       3. TYPOGRAPHY — headings get a teal accent
    ═══════════════════════════════════════════════════════════════════════ */
    h1 {
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em;
        color: #e8f4f8 !important;
        margin-bottom: 0.1rem !important;
    }
    h2 { font-size: 1.35rem !important; font-weight: 700 !important; }
    h3 { font-size: 1.1rem  !important; font-weight: 600 !important; }

    /* Teal accent bar left of every H2 section heading */
    h2 {
        border-left: 4px solid #00d4c8;
        padding-left: 0.6rem;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       4. DASHBOARD CARDS
       Used for the header area, tip banner, input panel, and results.
    ═══════════════════════════════════════════════════════════════════════ */
    .pg-card {
        background: rgba(19, 25, 41, 0.85);
        border: 1px solid rgba(0, 212, 200, 0.15);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 18px;
        backdrop-filter: blur(4px);
    }

    /* Glowing teal top-edge accent on the main header card */
    .pg-header-card {
        background: linear-gradient(135deg, #0d2233 0%, #0b0f19 60%);
        border: 1px solid rgba(0, 212, 200, 0.25);
        border-top: 3px solid #00d4c8;
        border-radius: 12px;
        padding: 22px 28px 18px 28px;
        margin-bottom: 20px;
    }

    /* Subtle teal glow on the header card */
    .pg-header-card::after {
        content: "";
        display: block;
        height: 1px;
        background: linear-gradient(90deg, transparent, #00d4c8 50%, transparent);
        margin-top: 16px;
        opacity: 0.4;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       5. TIP BANNER
    ═══════════════════════════════════════════════════════════════════════ */
    .tip-banner {
        background: linear-gradient(90deg, #0c2233 0%, #101e2e 100%);
        border: 1px solid rgba(0, 212, 200, 0.2);
        border-left: 4px solid #00d4c8;
        border-radius: 10px;
        padding: 13px 18px;
        font-size: 0.91rem;
        line-height: 1.6;
        color: #a8d8e8;          /* soft cyan — WCAG AA on #0c2233 */
        margin-bottom: 4px;
    }
    .tip-banner strong {
        color: #00d4c8;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        font-size: 0.75rem;
        display: block;
        margin-bottom: 4px;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       6. RISK SUMMARY CARD
    ═══════════════════════════════════════════════════════════════════════ */
    .risk-card {
        border-radius: 12px;
        padding: 20px 26px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .risk-badge {
        font-size: 2rem;
        line-height: 1;
        flex-shrink: 0;
    }
    .risk-label {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        line-height: 1.1;
    }
    .risk-score {
        font-size: 0.85rem;
        font-weight: 400;
        opacity: 0.75;
        margin-top: 2px;
    }

    /* Low risk */
    .risk-low {
        background: linear-gradient(135deg, #062318 0%, #0a2e1e 100%);
        border: 1px solid #1a6b3a;
        border-left: 5px solid #22c55e;
    }
    .risk-low .risk-label  { color: #4ade80; }   /* bright green — 7.1:1 on bg */
    .risk-low .risk-score  { color: #86efac; }

    /* Medium risk */
    .risk-medium {
        background: linear-gradient(135deg, #1c1200 0%, #251a04 100%);
        border: 1px solid #6b4a0a;
        border-left: 5px solid #f59e0b;
    }
    .risk-medium .risk-label { color: #fbbf24; } /* amber — 8.0:1 on bg */
    .risk-medium .risk-score { color: #fcd34d; }

    /* High risk */
    .risk-high {
        background: linear-gradient(135deg, #1a0505 0%, #220a0a 100%);
        border: 1px solid #7a1515;
        border-left: 5px solid #ef4444;
    }
    .risk-high .risk-label { color: #f87171; }   /* coral red — 6.9:1 on bg */
    .risk-high .risk-score { color: #fca5a5; }

    /* ═══════════════════════════════════════════════════════════════════════
       7. FINDING CARDS
       Each matched phishing clue gets its own card.
    ═══════════════════════════════════════════════════════════════════════ */
    .finding-card {
        background: linear-gradient(135deg, #1a1300 0%, #1e1700 100%);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-left: 4px solid #f59e0b;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .finding-title {
        font-size: 0.97rem;
        font-weight: 700;
        color: #fde68a;          /* soft amber-yellow — 8.6:1 on bg */
        margin: 0;
    }
    .pts-label {
        font-size: 0.78rem;
        font-weight: 500;
        color: #78716c;
        margin-left: 8px;
    }
    .finding-col-head {
        font-size: 0.72rem;
        font-weight: 700;
        color: #00d4c8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .finding-col-body {
        font-size: 0.88rem;
        color: #cbd5e1;
        line-height: 1.5;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       8. MISMATCH / STATUS BANNER
    ═══════════════════════════════════════════════════════════════════════ */
    .mismatch-banner {
        background: linear-gradient(90deg, #1c0f00 0%, #1f1200 100%);
        border: 1px solid rgba(251, 146, 60, 0.35);
        border-left: 4px solid #fb923c;
        border-radius: 10px;
        padding: 14px 18px;
        color: #fed7aa;
        font-size: 0.9rem;
        margin-bottom: 14px;
    }
    .mismatch-banner strong { color: #fb923c; }
    .mismatch-banner code   {
        background: rgba(251,146,60,0.12);
        border-radius: 4px;
        padding: 1px 5px;
        font-family: ui-monospace, "Cascadia Code", monospace;
        font-size: 0.85em;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       9. NEXT-STEPS CARDS
    ═══════════════════════════════════════════════════════════════════════ */
    .steps-card {
        border-radius: 10px;
        padding: 16px 20px;
        font-size: 0.9rem;
        line-height: 1.65;
        margin-bottom: 8px;
    }
    .steps-high {
        background: #1a0606;
        border: 1px solid rgba(239,68,68,0.3);
        border-left: 4px solid #ef4444;
        color: #fecaca;
    }
    .steps-medium {
        background: #1c1200;
        border: 1px solid rgba(245,158,11,0.3);
        border-left: 4px solid #f59e0b;
        color: #fef3c7;
    }
    .steps-low {
        background: #071814;
        border: 1px solid rgba(34,197,94,0.25);
        border-left: 4px solid #22c55e;
        color: #d1fae5;
    }
    .steps-card strong { font-weight: 700; }
    .steps-card ul {
        margin: 8px 0 0 0;
        padding-left: 1.2em;
    }
    .steps-card li { margin-bottom: 4px; }

    /* ═══════════════════════════════════════════════════════════════════════
       10. MONOSPACE — only for technical values (addresses, URLs, code)
    ═══════════════════════════════════════════════════════════════════════ */
    .mono {
        font-family: ui-monospace, "Cascadia Code", "Fira Code", monospace;
        font-size: 0.88em;
        background: rgba(0,212,200,0.07);
        border-radius: 4px;
        padding: 1px 6px;
        color: #a5f3fc;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       11. HORIZONTAL RULES
    ═══════════════════════════════════════════════════════════════════════ */
    hr {
        border: none !important;
        border-top: 1px solid rgba(0,212,200,0.1) !important;
        margin: 1.4rem 0 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       12. FOOTER
    ═══════════════════════════════════════════════════════════════════════ */
    .pg-footer {
        text-align: center;
        font-size: 12px;
        color: #3d4f5e;
        padding: 16px 0 8px 0;
        border-top: 1px solid rgba(0,212,200,0.12);
        letter-spacing: 0.04em;
    }
    .pg-footer strong { color: #00d4c8; }

    /* ═══════════════════════════════════════════════════════════════════════
       13. SECTION DIVIDER LABEL
    ═══════════════════════════════════════════════════════════════════════ */
    .section-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #00d4c8;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-label::after {
        content: "";
        flex: 1;
        height: 1px;
        background: rgba(0,212,200,0.18);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       14. INPUT PANEL TWEAKS
       Make the "or" separator and option labels feel intentional.
    ═══════════════════════════════════════════════════════════════════════ */
    .input-or {
        text-align: center;
        color: #3d5263;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 8px 0;
    }
    .option-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #00d4c8;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        margin-bottom: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# DATA — PHISHING CLUE DEFINITIONS
# =============================================================================
# Each clue has:
#   "id"          — unique short key used internally
#   "title"       — short name shown to the user
#   "pattern"     — regex to search for in the email body/headers
#   "points"      — risk points added when this clue is matched
#   "what"        — what was detected (shown to the user)
#   "why"         — why it may matter (educational)
#   "action"      — safe step the user can take
# =============================================================================
CLUE_DEFINITIONS = [
    {
        "id": "urgent_language",
        "title": "Urgent or threatening language",
        "pattern": (
            r"\b(urgent|immediately|act now|"
            r"your account (will be|has been) (suspended|closed|terminated|compromised)|"
            r"limited time|expires? (today|in \d+ hours?)|"
            r"last (chance|warning)|final notice|"
            r"failure to (respond|act|verify)|"
            r"you must (verify|confirm|update)|"
            r"account (locked|disabled))\b"
        ),
        "points": 25,
        "what": "The email uses language designed to make you act quickly without thinking.",
        "why": (
            "Phishers create artificial urgency so you react emotionally instead of "
            "stopping to question whether the email is real."
        ),
        "action": (
            "Pause. If you are worried, go directly to the company's official website "
            "by typing its address in your browser — do not use links in the email."
        ),
    },
    {
        "id": "password_request",
        "title": "Request for password or PIN",
        "pattern": (
            r"\b(enter|provide|confirm|update|verify|reset|submit)"
            r".{0,35}(password|passphrase|\bpin\b|passcode)\b"
        ),
        "points": 30,
        "what": "The email asks you to enter or confirm a password or PIN.",
        "why": (
            "Legitimate services never ask you to type your password "
            "into an email reply or an unfamiliar website."
        ),
        "action": (
            "Do not type your password. If a password reset is needed, "
            "start the process yourself from the official website."
        ),
    },
    {
        "id": "payment_request",
        "title": "Request for payment or financial details",
        "pattern": (
            r"\b(credit card|debit card|bank (account|details)|routing number|"
            r"payment (details|information|required)|billing information|"
            r"send money|wire transfer|gift card|cryptocurrency|bitcoin)\b"
        ),
        "points": 30,
        "what": "The email requests financial information or a payment.",
        "why": (
            "Requests for payment via gift cards, wire transfer, or cryptocurrency "
            "are classic fraud tactics — real companies do not ask for these by email."
        ),
        "action": (
            "Never send money or share financial details based on an unsolicited email. "
            "Verify the request by calling the organisation directly using a number from "
            "their official website."
        ),
    },
    {
        "id": "personal_info_request",
        "title": "Request for sensitive personal information",
        "pattern": (
            r"\b(social security|ssn|date of birth|home address|"
            r"mother'?s maiden name|national id|passport number|"
            r"driver'?s licen[sc]e)\b"
        ),
        "points": 25,
        "what": "The email asks for highly sensitive personal information.",
        "why": "This information is used for identity theft and fraud.",
        "action": (
            "Legitimate organisations rarely ask for details like your SSN or "
            "passport number over email. Do not provide them."
        ),
    },
    {
        "id": "link_present",
        "title": "Links present in the email",
        "pattern": r"https?://\S+",
        "points": 10,
        "what": "One or more URLs were detected in the email.",
        "why": (
            "Links in unexpected emails may lead to fake login pages designed "
            "to steal your credentials."
        ),
        "action": (
            "Do not click links in unexpected emails. If the email appears "
            "to come from a real company, navigate to that company's website "
            "directly instead."
        ),
    },
    {
        "id": "ip_link",
        "title": "Link using a raw IP address",
        "pattern": r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        "points": 35,
        "what": "A URL in the email points to a raw IP address rather than a domain name.",
        "why": (
            "Legitimate company websites use domain names. "
            "A link pointing to an IP address is a strong indicator of phishing."
        ),
        "action": "Do not click this link. Report the email as phishing to your email provider.",
    },
    {
        "id": "shortener_lookalike",
        "title": "URL shortener or lookalike domain",
        "pattern": (
            r"(bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|rb\.gy|short\.link|"
            r"paypa1\.com|arnazon\.com|g00gle\.com|micros0ft\.com|app1e\.com|"
            r"secure-[a-z]+-login\.com)"
        ),
        "points": 35,
        "what": "A URL shortener or a domain that closely mimics a well-known brand was detected.",
        "why": (
            "URL shorteners hide the real destination. Lookalike domains "
            "(e.g. 'paypa1.com' instead of 'paypal.com') trick people into "
            "thinking they are on a trusted website."
        ),
        "action": (
            "Do not click. Hover over any link to read the actual URL before "
            "deciding to visit it — and when in doubt, do not click."
        ),
    },
    {
        "id": "generic_greeting",
        "title": "Generic, impersonal greeting",
        "pattern": (
            r"\b(dear (customer|user|account holder|member|valued (customer|member|client))|"
            r"hello (customer|user)|greetings,?\s*(customer|user))\b"
        ),
        "points": 15,
        "what": "The email uses a generic greeting rather than your name.",
        "why": (
            "Mass phishing emails cannot address you personally, so they use "
            "generic openers. Legitimate services you have an account with "
            "usually know your name."
        ),
        "action": (
            "Treat impersonal greetings as a warning sign, especially when "
            "combined with urgent requests."
        ),
    },
    {
        "id": "attachment_mention",
        "title": "Unexpected attachment mentioned or present",
        "pattern": (
            r"\b(open|download|see|view|check).{0,25}"
            r"(attachment|attached (file|document|invoice|receipt)|"
            r"\.zip|\.exe|\.docm|\.xlsm|\.pdf)\b"
        ),
        "points": 20,
        "what": "The email mentions or instructs you to open an attachment.",
        "why": (
            "Malicious attachments — especially .exe, .zip, or macro-enabled "
            "Office files — are a primary way attackers install malware."
        ),
        "action": (
            "Do not open unexpected attachments. Verify with the sender "
            "through a separate, known channel before opening any file."
        ),
    },
    {
        "id": "authority_impersonation",
        "title": "Impersonation of IT, security, bank, or delivery service",
        "pattern": (
            r"\b(it (department|support|helpdesk|team)|security (team|department|alert)|"
            r"account (security|verification) team|technical support|system administrator|"
            r"your bank|fraud (department|team)|parcel|delivery (notification|update|attempt)|"
            r"package (could not be|failed to be) delivered)\b"
        ),
        "points": 20,
        "what": "The email claims to be from an authoritative source such as IT, security, a bank, or a courier.",
        "why": (
            "Phishers impersonate trusted authorities to lower your guard "
            "and make you more likely to follow instructions without questioning them."
        ),
        "action": (
            "Contact the organisation directly using contact details from their "
            "official website — never reply to the email or call numbers it provides."
        ),
    },
]

# =============================================================================
# DATA — FICTIONAL SAMPLE EMAILS  (for demo purposes only)
# =============================================================================
SAMPLE_EMAILS = [
    {
        "label": "🟢 Low Risk — Monthly newsletter (fictional)",
        "from": "newsletter@techtipsmonthly-example.com",
        "reply_to": "",
        "subject": "TechTips Monthly — July Edition",
        "body": (
            "Hi Sarah,\n\n"
            "Thank you for subscribing to the TechTips Monthly newsletter!\n\n"
            "This month we cover the top 10 productivity apps of the year. "
            "You can read the full article on our website at "
            "https://www.techtipsmonthly-example.com/july.\n\n"
            "To unsubscribe at any time, use the link at the bottom of this email.\n\n"
            "Best regards,\nThe TechTips Team"
        ),
    },
    {
        "label": "🟡 Medium Risk — Prize notification (fictional)",
        "from": "rewards@lucky-draw-promo-example.net",
        "reply_to": "collect@different-domain-example.com",
        "subject": "You have been selected — claim your prize",
        "body": (
            "Dear Customer,\n\n"
            "Congratulations! You have been selected as this week's lucky winner.\n\n"
            "To claim your prize, please confirm your home address and date of birth "
            "by replying to this email within 48 hours. "
            "Failure to respond will result in forfeiture of your prize.\n\n"
            "Best wishes,\nThe Rewards Team"
        ),
    },
    {
        "label": "🔴 High Risk — Account suspension scam (fictional)",
        "from": "security-alert@account-verify-example.xyz",
        "reply_to": "no-reply@account-verify-example.xyz",
        "subject": "URGENT: Your account has been compromised",
        "body": (
            "Dear valued customer,\n\n"
            "URGENT: Your account has been compromised. You must verify your details "
            "immediately or your account will be suspended within 24 hours.\n\n"
            "Please enter your password and credit card information at the link below:\n"
            "http://192.168.0.99/verify-account\n\n"
            "This is your final notice. Act now to avoid losing access.\n\n"
            "— Account Security Team"
        ),
    },
    {
        "label": "🔴 High Risk — Fake parcel delivery (fictional)",
        "from": "delivery@parcel-notify-example.ru",
        "reply_to": "tracking@parcel-notify-example.ru",
        "subject": "Your package could not be delivered",
        "body": (
            "Hello customer,\n\n"
            "Your package could not be delivered because of an incorrect address. "
            "A small redelivery fee of £1.99 is required.\n\n"
            "Please update your details and payment information here:\n"
            "https://bit.ly/2xF4k9Q\n\n"
            "Failure to respond within 24 hours will result in the parcel being returned.\n\n"
            "— Parcel Delivery Notification"
        ),
    },
]

# =============================================================================
# DATA — ROTATING AWARENESS TIPS
# One tip is chosen randomly at the start of each session and stays stable.
# =============================================================================
AWARENESS_TIPS = [
    (
        "Always check the sender's full email address, not just the display name. "
        "A name can say anything — the address after '@' is harder to fake."
    ),
    (
        "If an email asks you to click a link, navigate directly to the company's "
        "website instead. Type the address yourself rather than clicking."
    ),
    (
        "Hover over a link before clicking it. The real URL appears in your browser's "
        "status bar. If it looks different from what you expect, do not click."
    ),
    (
        "Verify unusual payment requests by calling the person or organisation "
        "directly using a phone number from their official website — not one in the email."
    ),
    (
        "Legitimate companies will never ask for your password by email. "
        "Any message doing so is almost certainly a phishing attempt."
    ),
    (
        "URL shorteners (bit.ly, tinyurl.com, etc.) hide the real destination. "
        "Be cautious when an email contains a shortened link."
    ),
    (
        "A professional-looking email is not proof it is real. "
        "Phishers copy logos, fonts, and layouts from genuine companies."
    ),
    (
        "If an email creates a strong sense of panic or urgency, slow down. "
        "That feeling is exactly what the attacker wants you to feel."
    ),
    (
        "Check whether the Reply-To address differs from the From address. "
        "A mismatch is a common trick to redirect your reply to the attacker."
    ),
    (
        "Never open unexpected attachments — especially .exe, .zip, or macro-enabled "
        "Office files — without verifying with the sender through a known channel."
    ),
]

# =============================================================================
# SESSION STATE INITIALISATION
# Streamlit reruns the script on every interaction, so we use session_state
# to keep values stable across those reruns.
# =============================================================================
if "tip_index" not in st.session_state:
    # Pick one random tip when the session starts; keep it for the whole session.
    st.session_state.tip_index = random.randint(0, len(AWARENESS_TIPS) - 1)

if "analysis_result" not in st.session_state:
    # Store the last analysis so the results tab can show it.
    st.session_state.analysis_result = None

if "input_source" not in st.session_state:
    # Track whether the last input came from a file upload or pasted text.
    st.session_state.input_source = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_text_from_html(raw_html: str) -> str:
    """
    Convert a raw HTML string into a readable plain-text approximation.
    We strip tags and decode HTML entities but never render the HTML live.
    This prevents scripts, images, or tracking pixels from running.
    """
    # Replace block-level tags with newlines so text is readable
    text = re.sub(r"<(br|p|div|li|tr|h[1-6])[^>]*>", "\n", raw_html, flags=re.IGNORECASE)
    # Strip all remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode HTML character entities (e.g. &amp; → &, &lt; → <)
    text = html.unescape(text)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_eml_file(file_bytes: bytes) -> dict | None:
    """
    Parse a raw .eml file (given as bytes) and return a dictionary with:
      "from"        — From header value (str)
      "reply_to"    — Reply-To header value (str)
      "subject"     — Subject header value (str)
      "body"        — Plain-text body (str)
      "attachments" — List of attachment filenames (list of str)
      "body_note"   — Optional note about how the body was obtained (str)
    Returns None if the file cannot be parsed.
    """
    try:
        # Use the modern EmailPolicy so we get unicode strings out cleanly
        msg = email.message_from_bytes(file_bytes, policy=policy.default)
    except Exception:
        return None

    from_addr  = msg.get("From", "")
    reply_to   = msg.get("Reply-To", "")
    subject    = msg.get("Subject", "")

    plain_body = ""
    html_body  = ""
    attachments = []
    body_note = ""

    # Walk every MIME part of the email
    for part in msg.walk():
        content_type = part.get_content_type()
        disposition  = str(part.get("Content-Disposition", ""))

        # Skip multipart wrappers — we only want leaf parts
        if part.is_multipart():
            continue

        # Collect attachment filenames (we never open or execute them)
        if "attachment" in disposition.lower():
            filename = part.get_filename() or "(unnamed)"
            attachments.append(filename)
            continue

        # Collect the plain-text body
        if content_type == "text/plain" and not plain_body:
            try:
                plain_body = part.get_content()  # returns a decoded str with policy.default
            except Exception:
                plain_body = ""

        # Collect the HTML body as a fallback
        if content_type == "text/html" and not html_body:
            try:
                html_body = part.get_content()
            except Exception:
                html_body = ""

    # Decide which body text to use for analysis
    if plain_body:
        body = plain_body
    elif html_body:
        body = extract_text_from_html(html_body)
        body_note = (
            "⚠️ This email contained only an HTML body. "
            "A plain-text version was extracted for analysis. "
            "HTML-only emails can hide their true content more easily."
        )
    else:
        body = ""
        body_note = "⚠️ No readable text body was found in this email."

    return {
        "from":        from_addr,
        "reply_to":    reply_to,
        "subject":     subject,
        "body":        body,
        "attachments": attachments,
        "body_note":   body_note,
    }


def check_sender_reply_to_mismatch(from_addr: str, reply_to: str) -> bool:
    """
    Return True if the From and Reply-To domains are different.
    A mismatch means your reply would go to a different address than the sender —
    a common trick used to harvest replies.
    """
    if not from_addr or not reply_to:
        return False

    # Extract the domain part after '@' from each address
    def get_domain(addr: str) -> str:
        match = re.search(r"@([\w.\-]+)", addr)
        return match.group(1).lower() if match else ""

    from_domain    = get_domain(from_addr)
    reply_to_domain = get_domain(reply_to)

    # Only flag if both domains are non-empty and genuinely different
    return bool(from_domain and reply_to_domain and from_domain != reply_to_domain)


def analyze_email_content(
    body: str,
    from_addr: str = "",
    reply_to: str = "",
    attachments: list | None = None,
) -> dict:
    """
    Run all phishing clue checks against the provided email content.

    Parameters
    ----------
    body        : The plain-text body of the email.
    from_addr   : The From header string.
    reply_to    : The Reply-To header string.
    attachments : List of attachment filenames found in the email.

    Returns a dictionary with:
      "score"          — int  0–100 (capped)
      "risk_level"     — str  "Low" | "Medium" | "High"
      "findings"       — list of finding dicts (one per triggered clue)
      "sender_mismatch"— bool  True if From/Reply-To domains differ
    """
    if attachments is None:
        attachments = []

    # The full text we search (body + headers combined so header checks work too)
    searchable_text = f"{from_addr}\n{reply_to}\n{body}"

    findings = []
    total_score = 0

    # --- Run each pattern-based clue ---
    for clue in CLUE_DEFINITIONS:
        if re.search(clue["pattern"], searchable_text, flags=re.IGNORECASE):
            findings.append(clue)
            total_score += clue["points"]

    # --- Extra clue: attachments actually present in the .eml file ---
    if attachments:
        risky_extensions = {".exe", ".zip", ".docm", ".xlsm", ".js", ".bat", ".vbs"}
        for fname in attachments:
            ext = "." + fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
            extra_points = 30 if ext in risky_extensions else 15
            findings.append(
                {
                    "id": f"attachment_{fname}",
                    "title": f"Attachment present: {fname}",
                    "points": extra_points,
                    "what": f"The email has an attachment named '{fname}'.",
                    "why": (
                        "Malicious attachments are a leading malware delivery method. "
                        + (
                            f"Files with the '{ext}' extension are particularly risky."
                            if ext in risky_extensions
                            else "Always verify unexpected attachments with the sender."
                        )
                    ),
                    "action": (
                        "Do not open this attachment unless you were expecting it "
                        "and have verified its origin through a separate, trusted channel."
                    ),
                }
            )
            total_score += extra_points

    # Cap the score so it never exceeds 100
    total_score = min(total_score, 100)

    # Map score to a risk level
    if total_score < 25:
        risk_level = "Low"
    elif total_score < 55:
        risk_level = "Medium"
    else:
        risk_level = "High"

    sender_mismatch = check_sender_reply_to_mismatch(from_addr, reply_to)

    return {
        "score":           total_score,
        "risk_level":      risk_level,
        "findings":        findings,
        "sender_mismatch": sender_mismatch,
    }


def extract_urls_from_text(text: str) -> list[str]:
    """
    Return a list of all URLs found in the text.
    We list them as plain strings only — we never fetch or open them.
    """
    return re.findall(r"https?://\S+", text)


def risk_css_class(risk_level: str) -> str:
    """Return the CSS class name for the risk card based on risk level."""
    return {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}.get(
        risk_level, "risk-low"
    )


def risk_emoji(risk_level: str) -> str:
    """Return an emoji representing the risk level."""
    return {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(risk_level, "⚪")


def build_report_text(
    result: dict,
    headers: dict,
    input_source: str,
) -> str:
    """
    Build a plain-text / Markdown report that the user can download.
    The original email body is NOT included by default.
    """
    lines = [
        "# PhishGuard — Email Analysis Report",
        f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Input source : {input_source}",
        "",
        "---",
        "",
        "## Risk Estimate",
        f"**{risk_emoji(result['risk_level'])} {result['risk_level']} Risk** — Score: {result['score']} / 100",
        "",
        "> This score is an educational indicator only, based on simple keyword rules.",
        "> A Low score does NOT mean the email is safe.",
        "",
        "---",
        "",
    ]

    # Add headers if available
    if any(headers.values()):
        lines += ["## Email Headers Reviewed", ""]
        for key, val in headers.items():
            if val:
                lines.append(f"- **{key}:** {val}")
        lines += ["", "---", ""]

    if result.get("sender_mismatch"):
        lines += [
            "## ⚠️ Sender / Reply-To Mismatch",
            "The From and Reply-To addresses belong to different domains.",
            "Your reply would go to a different address than the apparent sender.",
            "",
            "---",
            "",
        ]

    lines += ["## Findings", ""]
    if result["findings"]:
        for i, f in enumerate(result["findings"], 1):
            lines += [
                f"### {i}. {f['title']}",
                f"**What was detected:** {f['what']}",
                f"**Why it may matter:** {f['why']}",
                f"**Suggested action:** {f['action']}",
                "",
            ]
    else:
        lines += [
            "No phishing clues were detected by these basic checks.",
            "This does not mean the email is safe.",
            "",
        ]

    lines += [
        "---",
        "",
        "_PhishGuard is an educational tool. "
        "For genuine security concerns, contact your IT or security team._",
    ]

    return "\n".join(lines)


# =============================================================================
# APP LAYOUT
# =============================================================================

# ── Header card ───────────────────────────────────────────────────────────────
st.markdown(
    "<div class='pg-header-card'>"
    "<h1>🛡️ PhishGuard</h1>"
    "<p style='color:#8aabb8; font-size:0.95rem; margin:6px 0 0 0;'>"
    "Educational phishing-awareness tool &nbsp;·&nbsp; "
    "Paste email text or upload a <code style='font-family:monospace; "
    "background:rgba(0,212,200,0.08); padding:1px 5px; border-radius:3px;'>.eml</code> "
    "file to highlight common warning signs."
    "</p>"
    "<p style='color:#4a6272; font-size:0.78rem; margin:8px 0 0 0; font-style:italic;'>"
    "⚠ Learning aid only — a Low score does not mean an email is safe."
    "</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ── Rotating awareness tip ────────────────────────────────────────────────────
st.markdown(
    f"<div class='tip-banner'>"
    f"<strong>💡 Tip of the session</strong>"
    f"{AWARENESS_TIPS[st.session_state.tip_index]}"
    f"</div>",
    unsafe_allow_html=True,
)

# ── Privacy notice ────────────────────────────────────────────────────────────
with st.expander("🔒 Privacy & Safety Notice — read before uploading anything"):
    st.warning(
        "**Do not upload or paste real confidential emails.**\n\n"
        "- Do not include real passwords, payment details, or personal information.\n"
        "- Uploaded or pasted email content is used only within your current browser "
        "session. It is never saved, logged, or transmitted.\n"
        "- Use the fictional demo samples if you want to explore the tool safely.\n"
        "- On shared or public computers, close the browser tab when you are done."
    )

st.divider()

# =============================================================================
# THREE TABS: Provide Email | Review Findings | Learn More
# =============================================================================
tab_provide, tab_results, tab_learn = st.tabs(
    ["📨 Provide Email", "📊 Review Findings", "📚 Learn More"]
)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — PROVIDE EMAIL
# ─────────────────────────────────────────────────────────────────────────────
with tab_provide:

    st.markdown("<div class='section-label'>Provide Email</div>", unsafe_allow_html=True)

    # ── Option A: upload a .eml file ─────────────────────────────────────────
    st.markdown("<div class='option-label'>Option A — Upload a .eml file (max 200 KB)</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Upload .eml file",
        type=["eml"],
        help="Maximum file size: 200 KB. Only .eml files are accepted.",
        label_visibility="collapsed",
    )

    st.markdown("<div class='input-or'>— or —</div>", unsafe_allow_html=True)

    # ── Option B: paste text directly ────────────────────────────────────────
    st.markdown("<div class='option-label'>Option B — Paste email text</div>", unsafe_allow_html=True)

    # Allow demo samples to pre-fill the text area
    sample_labels = ["— Load a fictional demo sample —"] + [s["label"] for s in SAMPLE_EMAILS]
    chosen_sample_label = st.selectbox(
        "Load a fictional demo sample:",
        sample_labels,
        key="sample_select",
        help="All samples are entirely fictional and created for educational purposes.",
    )

    prefill_text = ""
    prefill_headers = {"From": "", "Reply-To": "", "Subject": ""}

    if chosen_sample_label != sample_labels[0]:
        # Find the matching sample and pre-fill both the text area and header fields
        for sample in SAMPLE_EMAILS:
            if sample["label"] == chosen_sample_label:
                prefill_text = sample["body"]
                prefill_headers = {
                    "From":     sample.get("from", ""),
                    "Reply-To": sample.get("reply_to", ""),
                    "Subject":  sample.get("subject", ""),
                }
                break

    pasted_text = st.text_area(
        "Paste email body here:",
        value=prefill_text,
        height=200,
        placeholder="Paste the body of the email here…",
        label_visibility="collapsed",
    )

    # Optional header fields for pasted-text mode
    with st.expander("Add optional header information (From, Reply-To, Subject)"):
        st.caption(
            "These are optional. Filling them in allows PhishGuard to check for "
            "sender/Reply-To mismatches and include header context in the report."
        )
        h_from     = st.text_input("From:",     value=prefill_headers["From"],     placeholder="sender@example.com")
        h_reply_to = st.text_input("Reply-To:", value=prefill_headers["Reply-To"], placeholder="other@example.com")
        h_subject  = st.text_input("Subject:",  value=prefill_headers["Subject"],  placeholder="Email subject line")

    # ── Conflict warning ─────────────────────────────────────────────────────
    if uploaded_file and pasted_text.strip():
        st.warning(
            "⚠️ Both a file upload and pasted text are present. "
            "Select which one to analyse:"
        )
        use_choice = st.radio(
            "Analyse:",
            ["Uploaded .eml file", "Pasted text"],
            horizontal=True,
            key="conflict_choice",
        )
    else:
        use_choice = None  # No conflict — we'll figure it out automatically below

    st.markdown("")  # spacing
    analyse_button = st.button("🔍 Analyse Email", type="primary", use_container_width=True)

    if analyse_button:
        # ── Determine which input to use ─────────────────────────────────────
        use_file   = False
        use_pasted = False

        if use_choice == "Uploaded .eml file":
            use_file = True
        elif use_choice == "Pasted text":
            use_pasted = True
        elif uploaded_file:
            use_file = True
        elif pasted_text.strip():
            use_pasted = True

        # ── Handle empty input ────────────────────────────────────────────────
        if not use_file and not use_pasted:
            st.info(
                "Please upload a .eml file or paste email text before clicking Analyse."
            )
            st.stop()

        # ── Analyse uploaded .eml ─────────────────────────────────────────────
        if use_file:
            # This check satisfies the type checker: st.file_uploader returns
            # UploadedFile | None, but we only reach here when a file is present.
            if uploaded_file is None:
                st.error("No file was found. Please upload a .eml file and try again.")
                st.stop()

            file_bytes = uploaded_file.read()

            # Enforce a 200 KB size limit
            if len(file_bytes) > 200 * 1024:
                st.error(
                    "The uploaded file exceeds the 200 KB limit. "
                    "Please use a smaller file or paste the email text instead."
                )
                st.stop()

            parsed = parse_eml_file(file_bytes)
            if parsed is None:
                st.error(
                    "PhishGuard could not parse this file. "
                    "Make sure it is a valid .eml file and try again. "
                    "If the file is heavily encoded or malformed, "
                    "try copying and pasting the visible email text instead."
                )
                st.stop()

            body        = parsed["body"]
            from_addr   = parsed["from"]
            reply_to    = parsed["reply_to"]
            subject     = parsed["subject"]
            attachments = parsed["attachments"]
            body_note   = parsed["body_note"]
            source_label = f"Uploaded file: {uploaded_file.name}"

            if body_note:
                st.info(body_note)

        # ── Analyse pasted text ───────────────────────────────────────────────
        else:
            body        = pasted_text.strip()
            from_addr   = h_from.strip()
            reply_to    = h_reply_to.strip()
            subject     = h_subject.strip()
            attachments = []
            source_label = "Pasted text"

        # ── Run the analysis ──────────────────────────────────────────────────
        result = analyze_email_content(
            body=body,
            from_addr=from_addr,
            reply_to=reply_to,
            attachments=attachments,
        )

        # Store everything in session state so the Results tab can display it
        st.session_state.analysis_result = result
        st.session_state.input_source    = source_label
        st.session_state.headers = {
            "From":     from_addr,
            "Reply-To": reply_to,
            "Subject":  subject,
        }
        st.session_state.body = body
        st.session_state.urls = extract_urls_from_text(body)

        st.success("✅ Analysis complete — open the **Review Findings** tab to see the results.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — REVIEW FINDINGS
# ─────────────────────────────────────────────────────────────────────────────
with tab_results:

    result = st.session_state.get("analysis_result")

    if result is None:
        st.info("Provide an email on the **Provide Email** tab and click Analyse to see results here.")
        st.stop()

    score      = result["score"]
    risk       = result["risk_level"]
    findings   = result["findings"]
    mismatch   = result["sender_mismatch"]
    headers    = st.session_state.get("headers", {})
    urls       = st.session_state.get("urls", [])
    source     = st.session_state.get("input_source", "")
    css_class  = risk_css_class(risk)
    emoji      = risk_emoji(risk)

    st.markdown("<div class='section-label'>Analysis Results</div>", unsafe_allow_html=True)
    st.caption(f"Source: {source}")

    # ── Risk card ─────────────────────────────────────────────────────────────
    # The card uses nested divs so the badge, label, and score line up cleanly.
    st.markdown(
        f"<div class='risk-card {css_class}'>"
        f"<div class='risk-badge'>{emoji}</div>"
        f"<div>"
        f"<div class='risk-label'>{risk} Risk</div>"
        f"<div class='risk-score'>Score: {score} / 100 &nbsp;·&nbsp; "
        f"Educational indicator only — not a security verdict</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.progress(score / 100)

    # ── Reviewed headers ─────────────────────────────────────────────────────
    if any(headers.values()):
        with st.expander("📋 Email headers reviewed"):
            for key, val in headers.items():
                if val:
                    # Use .mono class so addresses render in monospace, not the page font
                    st.markdown(
                        f"**{key}:** <span class='mono'>{val}</span>",
                        unsafe_allow_html=True,
                    )

    # ── Sender / Reply-To mismatch alert ─────────────────────────────────────
    if mismatch:
        st.markdown(
            "<div class='mismatch-banner'>"
            "<strong>⚠ Sender / Reply-To mismatch detected</strong><br>"
            f"From: <code>{headers.get('From', '')}</code><br>"
            f"Reply-To: <code>{headers.get('Reply-To', '')}</code><br><br>"
            "These belong to different domains. If you reply, your message goes "
            "to a different address than the apparent sender — a common phishing trick."
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Findings ─────────────────────────────────────────────────────────────
    st.divider()
    if findings:
        st.markdown(
            f"<div class='section-label'>🚩 {len(findings)} clue(s) detected</div>",
            unsafe_allow_html=True,
        )
        for finding in findings:
            # Title row — styled finding card header
            st.markdown(
                f"<div class='finding-card'>"
                f"<span class='finding-title'>{finding['title']}</span>"
                f"<span class='pts-label'>(+{finding['points']} pts)</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            # Three-column detail below each card
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(
                    "<div class='finding-col-head'>What was detected</div>"
                    f"<div class='finding-col-body'>{finding['what']}</div>",
                    unsafe_allow_html=True,
                )
            with col_b:
                st.markdown(
                    "<div class='finding-col-head'>Why it may matter</div>"
                    f"<div class='finding-col-body'>{finding['why']}</div>",
                    unsafe_allow_html=True,
                )
            with col_c:
                st.markdown(
                    "<div class='finding-col-head'>Safe action</div>"
                    f"<div class='finding-col-body'>{finding['action']}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("---")
    else:
        st.success(
            "✅ No clues were detected by these basic checks.  \n"
            "_Remember: this does not mean the email is safe. "
            "Sophisticated phishing emails can pass simple pattern checks easily._"
        )

    # ── URLs found ────────────────────────────────────────────────────────────
    if urls:
        with st.expander(f"🔗 {len(urls)} URL(s) found — listed as plain text only"):
            st.caption(
                "These URLs are displayed as text only. "
                "PhishGuard never fetches, visits, or previews them. "
                "Do not click them if the email is suspicious."
            )
            for url in urls:
                # Show as code block (not a clickable link) to discourage accidental clicks
                st.code(url, language=None)

    # ── Recommended next steps ────────────────────────────────────────────────
    st.divider()
    st.markdown(
        "<div class='section-label'>🛡 Recommended Next Steps</div>",
        unsafe_allow_html=True,
    )

    if risk == "High":
        st.markdown(
            "<div class='steps-card steps-high'>"
            "<strong>Multiple strong phishing indicators were detected.</strong>"
            "<ul>"
            "<li>Do not click any links or open any attachments in this email.</li>"
            "<li>Do not reply to the email or call any phone numbers it provides.</li>"
            "<li>Contact the apparent sender through their official website to verify.</li>"
            "<li>Report the email as phishing to your email provider.</li>"
            "<li>If you already clicked a link or shared information, change your passwords "
            "and contact your IT or security team immediately.</li>"
            "</ul>"
            "</div>",
            unsafe_allow_html=True,
        )
    elif risk == "Medium":
        st.markdown(
            "<div class='steps-card steps-medium'>"
            "<strong>Some phishing indicators detected — treat with caution.</strong>"
            "<ul>"
            "<li>Verify the sender's identity before responding or clicking anything.</li>"
            "<li>Navigate to the company's website directly instead of using email links.</li>"
            "<li>Ask your IT or security team to review the email if in doubt.</li>"
            "</ul>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='steps-card steps-low'>"
            "<strong>No strong phishing indicators detected by these basic checks.</strong>"
            "<ul>"
            "<li>Remain cautious — sophisticated phishing can look very convincing.</li>"
            "<li>If something feels unusual, verify through an official channel before acting.</li>"
            "</ul>"
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Download report ───────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        "<div class='section-label'>📥 Download Analysis Report</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "The report contains the risk estimate and findings. "
        "The original email body is not included. "
        "If findings mention specific subject lines or domains, "
        "be aware the report may contain details from the email."
    )

    report_text = build_report_text(
        result=result,
        headers=headers,
        input_source=source,
    )

    st.download_button(
        label="Download report (.md)",
        data=report_text,
        file_name="phishguard_report.md",
        mime="text/markdown",
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — LEARN MORE
# ─────────────────────────────────────────────────────────────────────────────
with tab_learn:

    st.markdown("<div class='section-label'>Phishing Awareness — Key Concepts</div>", unsafe_allow_html=True)

    with st.expander("What is phishing?"):
        st.write(
            "Phishing is a type of social-engineering attack where someone pretends to be "
            "a trusted person or organisation to trick you into handing over sensitive "
            "information — such as passwords, credit-card numbers, or personal details — "
            "or into installing malware on your device.\n\n"
            "Most phishing happens over email, but it also occurs via text messages "
            "(smishing), phone calls (vishing), and social media."
        )

    with st.expander("What clues does PhishGuard check for?"):
        st.markdown(
            "PhishGuard checks for the following patterns using keyword rules:  \n"
            + "\n".join(f"- **{c['title']}**" for c in CLUE_DEFINITIONS)
            + "\n\n"
            "It also checks whether the From and Reply-To addresses belong to different domains, "
            "and reports any attachment filenames found in uploaded .eml files."
        )

    with st.expander("How is the risk score calculated?"):
        st.write(
            "Each matched clue adds a set number of points to the score. "
            "The total is capped at 100. "
            "Scores below 25 are Low risk, 25–54 are Medium, and 55 or above are High.\n\n"
            "The thresholds are simple and educational — they are not calibrated "
            "against a real dataset of phishing emails."
        )
        st.markdown("| Clue | Points |")
        st.markdown("|---|---|")
        for c in CLUE_DEFINITIONS:
            st.markdown(f"| {c['title']} | +{c['points']} |")

    with st.expander("What are the limitations of this tool?"):
        st.write(
            "PhishGuard uses very basic keyword and pattern matching. Its limitations include:\n\n"
            "- **False negatives:** A well-crafted phishing email that avoids the checked "
            "keywords will score Low. A Low score does NOT mean an email is safe.\n"
            "- **False positives:** Legitimate emails (e.g. a real password reset, a bank "
            "statement) may trigger some clues.\n"
            "- **No URL fetching:** PhishGuard cannot visit links to check where they lead.\n"
            "- **English only:** All patterns are written for English-language emails.\n"
            "- **No sender verification:** PhishGuard cannot check email headers for "
            "SPF, DKIM, or DMARC records — those require a real email security tool.\n"
            "- **No attachment scanning:** Attached files are never opened or scanned."
        )

    with st.expander("What should I do if I think an email is a phishing attempt?"):
        st.write(
            "1. **Do not click any links** in the email.\n"
            "2. **Do not open attachments.**\n"
            "3. **Do not reply** or call any number provided in the email.\n"
            "4. If the email appears to come from a real company, contact that company "
            "directly using contact details from their official website.\n"
            "5. **Report** the email as phishing to your email provider "
            "(most have a 'Report phishing' or 'Report spam' button).\n"
            "6. If you have already clicked a link or provided information, "
            "change your passwords immediately and notify your IT or security team."
        )

    with st.expander("All awareness tips"):
        for i, tip in enumerate(AWARENESS_TIPS, 1):
            st.markdown(f"**{i}.** {tip}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div class='pg-footer'>"
    "<strong>PhishGuard</strong> &nbsp;·&nbsp; Educational use only &nbsp;·&nbsp; "
    "Not a substitute for professional cybersecurity tools &nbsp;·&nbsp; "
    "All sample emails are entirely fictional"
    "</div>",
    unsafe_allow_html=True,
)
