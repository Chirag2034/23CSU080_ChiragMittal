# ============================================================
# VERIDIAN CORP - INTERNAL IT SERVICE AGENT
# AIONOS Assignment 2
# ============================================================

from datetime import datetime
import uuid
import re

from knowledge_base import KNOWLEDGE_BASE


# ============================================================
# RESULT BUILDER
# ============================================================

def make_result(
    intent,
    decision,
    response,
    sources=None,
    confidence="High",
    action="Respond",
    needs_ticket=False,
    priority="Normal",
    assigned_to="IT Support",
    follow_up=None,
):
    """
    Creates a consistent structured response from the agent.
    """

    return {
        "intent": intent,
        "decision": decision,
        "response": response,
        "sources": sources or [],
        "confidence": confidence,
        "action": action,
        "needs_ticket": needs_ticket,
        "priority": priority,
        "assigned_to": assigned_to,
        "follow_up": follow_up,
    }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def contains_any(text, keywords):
    """
    Returns True if any keyword is found in the supplied text.
    """
    return any(keyword in text for keyword in keywords)


def extract_failed_attempts(text):
    """
    Attempts to identify the number of failed password attempts.

    Example:
        "tried my password 6 times" -> 6
    """

    patterns = [
        r"(\d+)\s*times",
        r"(\d+)\s*attempts",
        r"tried.*?(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None

    return None


# ============================================================
# MAIN AGENT
# ============================================================

def analyze_request(message):
    """
    Analyze an employee IT request and return a policy-grounded
    decision.

    The agent must not invent policies that are not available
    in the supplied Veridian Corp knowledge base.
    """

    if not message or not message.strip():

        return make_result(
            intent="Empty Request",
            decision="Ask Follow-up",
            response=(
                "Please describe the IT issue you are experiencing "
                "so I can determine the appropriate next action."
            ),
            confidence="Low",
            action="Request more information",
            follow_up="What IT issue are you experiencing?",
        )

    text = message.lower().strip()

    # ========================================================
    # 1. SECURITY INCIDENT / PHISHING
    # ========================================================

    if contains_any(
        text,
        [
            "phishing",
            "phish",
            "suspicious email",
            "suspicious link",
            "malware",
            "unauthorized access",
            "unauthorised access",
            "stolen credentials",
        ],
    ):

        return make_result(
            intent="Security Incident",
            decision="Escalate Immediately",
            response=(
                "This may be a security incident. Report it immediately "
                "to security@veridian-corp.example. Do not forward the "
                "suspected phishing email or security-related content "
                "to other employees."
            ),
            sources=["KB-09"],
            confidence="High",
            action="Immediate Security escalation",
            needs_ticket=True,
            priority="Critical",
            assigned_to="IT Security",
        )

    # ========================================================
    # 2. PASSWORD / ACCOUNT LOCKOUT
    # ========================================================

    if contains_any(
        text,
        [
            "password",
            "locked out",
            "account locked",
            "login locked",
            "failed attempts",
        ],
    ):

        failed_attempts = extract_failed_attempts(text)

        if (
            "locked out" in text
            or "account locked" in text
            or (
                failed_attempts is not None
                and failed_attempts >= 5
            )
        ):

            return make_result(
                intent="Account Lockout",
                decision="Manual IT Unlock Required",
                response=(
                    "Your account appears to be locked. Under KB-01, "
                    "an account locked after 5 failed password attempts "
                    "requires IT to unlock it manually. No approval is "
                    "required."
                ),
                sources=["KB-01"],
                confidence="High",
                action="Route to IT for manual account unlock",
                needs_ticket=True,
                priority="High",
                assigned_to="IT Support",
            )

        return make_result(
            intent="Password Reset",
            decision="Self-Service Resolution",
            response=(
                "You can reset your password using the self-service "
                "portal. No approval is required."
            ),
            sources=["KB-01"],
            confidence="High",
            action="Use self-service password reset",
            needs_ticket=False,
            priority="Normal",
        )

    # ========================================================
    # 3. GUEST WI-FI
    # ========================================================

    if (
        "guest" in text
        and contains_any(
            text,
            [
                "wifi",
                "wi-fi",
                "wireless",
                "internet",
            ],
        )
    ):

        return make_result(
            intent="Guest Wi-Fi Access",
            decision="Self-Service Resolution",
            response=(
                "Guest Wi-Fi credentials can be generated by any "
                "employee from the front-desk kiosk. The credentials "
                "are valid for 24 hours. No IT ticket is required."
            ),
            sources=["KB-07"],
            confidence="High",
            action="Generate credentials at front-desk kiosk",
            needs_ticket=False,
            priority="Normal",
        )

    # ========================================================
    # 4. VPN ACCESS
    # ========================================================

    if "vpn" in text:

        # Contractor VPN request
        if contains_any(
            text,
            [
                "contractor",
                "consultant",
            ],
        ):

            return make_result(
                intent="Contractor VPN Access",
                decision="Manager Approval Required",
                response=(
                    "Contractors require manager approval before VPN "
                    "access can be granted. The approval must be submitted "
                    "through the access request form."
                ),
                sources=["KB-02"],
                confidence="High",
                action="Obtain manager approval via access request form",
                needs_ticket=True,
                priority="Normal",
                assigned_to="Access Management",
            )

        # Expired VPN credentials
        if contains_any(
            text,
            [
                "expired",
                "credentials expired",
                "credential expired",
                "renew",
                "renewal",
            ],
        ):

            return make_result(
                intent="Expired VPN Credentials",
                decision="Employee Renewal Required",
                response=(
                    "VPN credentials expire every 90 days and must be "
                    "renewed by the employee."
                ),
                sources=["KB-02"],
                confidence="High",
                action="Renew VPN credentials",
                needs_ticket=False,
                priority="Normal",
            )

        # General VPN request
        return make_result(
            intent="VPN Access",
            decision="Policy Guidance",
            response=(
                "VPN access is automatically granted to full-time "
                "employees. Contractors require manager approval through "
                "the access request form."
            ),
            sources=["KB-02"],
            confidence="High",
            action="Determine employee type",
            needs_ticket=False,
            follow_up=(
                "Are you a full-time employee or a contractor?"
            ),
        )

    # ========================================================
    # 5. SOFTWARE INSTALLATION
    # ========================================================

    if contains_any(
        text,
        [
            "install",
            "software",
            "application",
            "browser extension",
            "extension",
            "tool",
        ],
    ):

        # ----------------------------------------------------
        # Explicitly NON-CATALOG software
        # ----------------------------------------------------

        if contains_any(
            text,
            [
                "not in the catalog",
                "not in catalog",
                "not in the software catalog",
                "not in software catalog",
                "not in the approved catalog",
                "not in approved catalog",
                "not listed in the catalog",
                "not listed in catalog",
                "not listed in the software catalog",
                "not listed in software catalog",
                "non-catalog",
                "non catalog",
                "outside the catalog",
                "outside approved catalog",
                "outside the approved catalog",
            ],
        ):

            return make_result(
                intent="Non-Catalog Software Installation",
                decision="IT Security Review Required",
                response=(
                    "The requested software is not in the approved "
                    "catalog. Under KB-04, non-catalog software requires "
                    "IT Security review. The stated review time is "
                    "3-5 business days."
                ),
                sources=["KB-04"],
                confidence="High",
                action="Route request to IT Security review",
                needs_ticket=True,
                priority="Normal",
                assigned_to="IT Security",
            )

        # ----------------------------------------------------
        # Explicitly APPROVED / CATALOG software
        # ----------------------------------------------------

        if contains_any(
            text,
            [
                "in the approved catalog",
                "in approved catalog",
                "listed in the approved catalog",
                "listed in approved catalog",
                "approved catalog software",
                "approved software catalog",
                "approved software",
            ],
        ):

            return make_result(
                intent="Approved Software Installation",
                decision="Self-Service Installation",
                response=(
                    "The requested software is listed in the approved "
                    "software catalog. Under KB-04, approved-catalog "
                    "software can be self-installed."
                ),
                sources=["KB-04"],
                confidence="High",
                action="Install software using the approved catalog",
                needs_ticket=False,
                priority="Normal",
            )

        # ----------------------------------------------------
        # Browser extension - catalog status unknown
        # ----------------------------------------------------

        if "browser extension" in text or "extension" in text:

            return make_result(
                intent="Software Installation",
                decision="Clarification Required",
                response=(
                    "Software in the approved catalog can be "
                    "self-installed, while non-catalog software requires "
                    "IT Security review. I need to know whether this "
                    "browser extension is listed in the approved catalog."
                ),
                sources=["KB-04"],
                confidence="Medium",
                action="Ask catalog-status follow-up",
                needs_ticket=False,
                follow_up=(
                    "Is the requested browser extension listed in the "
                    "approved software catalog?"
                ),
            )

        # ----------------------------------------------------
        # Generic software request - status unknown
        # ----------------------------------------------------

        return make_result(
            intent="Software Installation",
            decision="Clarification Required",
            response=(
                "Approved-catalog software can be self-installed. "
                "Non-catalog software requires IT Security review."
            ),
            sources=["KB-04"],
            confidence="Medium",
            action="Determine catalog status",
            needs_ticket=False,
            follow_up=(
                "Is the requested software listed in the approved catalog?"
            ),
        )

    # ========================================================
    # 6. PRINTER PROBLEM
    # ========================================================

    if contains_any(
        text,
        [
            "printer",
            "paper jam",
            "printing",
            "print spooler",
        ],
    ):

        return make_result(
            intent="Printer Issue",
            decision="Troubleshoot First",
            response=(
                "First check the printer queue and restart the print "
                "spooler. If the issue persists after the restart, "
                "log a ticket with the printer's asset tag."
            ),
            sources=["KB-05"],
            confidence="High",
            action="Check queue and restart print spooler",
            needs_ticket=False,
            priority="Normal",
            follow_up=(
                "If the problem continues after restarting the spooler, "
                "please provide the printer asset tag."
            ),
        )

    # ========================================================
    # 7. EMAIL MAILBOX QUOTA
    # ========================================================

    if contains_any(
        text,
        [
            "mailbox",
            "quota",
            "email full",
            "mail full",
            "mailbox full",
            "can't send emails",
            "cannot send emails",
        ],
    ):

        return make_result(
            intent="Mailbox Quota",
            decision="Archive Mail / Approval for Increase",
            response=(
                "The default mailbox quota is 25GB. Employees nearing "
                "the limit should first archive old mail. Any increase "
                "beyond 25GB requires manager approval and is capped "
                "at 50GB."
            ),
            sources=["KB-06"],
            confidence="High",
            action="Archive old mail first",
            needs_ticket=False,
            priority="Normal",
            follow_up=(
                "If archiving is insufficient, do you want to request "
                "a quota increase with manager approval?"
            ),
        )

    # ========================================================
    # 8. WORK-FROM-HOME EQUIPMENT
    # ========================================================

    if contains_any(
        text,
        [
            "work from home",
            "working from home",
            "home office",
            "remote work",
            "remotely",
        ],
    ):

        return make_result(
            intent="Work-From-Home Equipment",
            decision="Manager and Finance Approval Required",
            response=(
                "Employees working remotely more than 3 days per week "
                "are eligible for a one-time home-office equipment "
                "allowance for items such as a chair or monitor. "
                "Manager sign-off and Finance processing are required. "
                "IT handles equipment shipping only after approval."
            ),
            sources=["KB-10"],
            confidence="High",
            action="Manager approval → Finance processing → IT shipping",
            needs_ticket=True,
            priority="Normal",
            assigned_to="Finance / IT",
        )

    # ========================================================
    # 9. EXPENSE MANAGEMENT SOFTWARE
    # ========================================================

    if contains_any(
        text,
        [
            "expense tool",
            "expense software",
            "expense management",
        ],
    ):

        if contains_any(
            text,
            [
                "can't log",
                "cannot log",
                "invalid credentials",
                "login",
                "technical",
            ],
        ):

            return make_result(
                intent="Expense Tool Login Issue",
                decision="IT Can Assist if Account Exists",
                response=(
                    "Finance grants access to the expense management "
                    "tool. IT can assist with login or technical issues "
                    "once an account already exists."
                ),
                sources=["KB-08"],
                confidence="High",
                action="Confirm existing Finance account",
                needs_ticket=False,
                assigned_to="IT Support",
                follow_up=(
                    "Do you already have an active expense management "
                    "account provided by Finance?"
                ),
            )

        return make_result(
            intent="Expense Software Access",
            decision="Route to Finance",
            response=(
                "Access to the expense management tool is granted by "
                "Finance, not IT. IT can assist only with login or "
                "technical problems after an account already exists."
            ),
            sources=["KB-08"],
            confidence="High",
            action="Route access request to Finance",
            needs_ticket=False,
            assigned_to="Finance",
        )

    # ========================================================
    # 10. LAPTOP / HARDWARE
    # ========================================================

    if contains_any(
        text,
        [
            "laptop",
            "laptop screen",
            "screen flicker",
            "screen is flickering",
            "hardware",
        ],
    ):

        # Detect obvious 3+ year laptop case
        older_laptop = contains_any(
            text,
            [
                "3.5 years",
                "3.2 years",
                "3 years",
                "3 year",
                "three years",
                "4 years",
                "4 year",
                "four years",
            ],
        )

        if older_laptop:

            return make_result(
                intent="Laptop Replacement / Hardware Failure",
                decision="Policy Conflict — Human Review Required",
                response=(
                    "The supplied sources contain conflicting laptop "
                    "replacement guidance. KB-03 states that laptops "
                    "are eligible for replacement after 3 years or "
                    "earlier for verified hardware failure. However, "
                    "the Asset Management Policy specifies a standard "
                    "4-year refresh cycle and requires Finance sign-off "
                    "in addition to IT approval for early replacement. "
                    "I will not invent a policy decision, so this case "
                    "requires human review."
                ),
                sources=["KB-03", "ASSET-01"],
                confidence="High",
                action="Route to IT and Finance for policy review",
                needs_ticket=True,
                priority="High",
                assigned_to="IT / Finance",
            )

        # Hardware failure under 3 years / age unknown
        return make_result(
            intent="Laptop Hardware Issue",
            decision="Hardware Diagnosis Required",
            response=(
                "The laptop should first be assessed for verified "
                "hardware failure. KB-03 allows earlier replacement "
                "for verified hardware failure, while the Asset "
                "Management Policy requires additional approval for "
                "replacement outside the standard refresh cycle."
            ),
            sources=["KB-03", "ASSET-01"],
            confidence="High",
            action="IT hardware diagnosis",
            needs_ticket=True,
            priority="High",
            assigned_to="IT Hardware Support",
        )

    # ========================================================
    # 11. PRIVILEGED / ADMIN ACCESS
    # ========================================================

    if contains_any(
        text,
        [
            "admin access",
            "administrator access",
            "privileged access",
            "server admin",
            "finance reporting server",
        ],
    ):

        return make_result(
            intent="Privileged Access Request",
            decision="Escalate — No Supporting Policy",
            response=(
                "The supplied knowledge base does not provide a policy "
                "authorizing this privileged access request. I cannot "
                "approve or invent an access rule. The request must be "
                "reviewed by an authorized human."
            ),
            sources=[],
            confidence="High",
            action="Escalate for authorization review",
            needs_ticket=True,
            priority="High",
            assigned_to="IT Access Management",
        )

    # ========================================================
    # 12. VERY VAGUE REQUEST
    # ========================================================

    vague_phrases = [
        "not working",
        "its not working",
        "it's not working",
        "help",
        "help me",
        "can you help",
        "hey can you help",
    ]

    if (
        len(text.split()) <= 7
        or text in vague_phrases
        or (
            "not working" in text
            and not contains_any(
                text,
                [
                    "vpn",
                    "printer",
                    "laptop",
                    "email",
                    "mailbox",
                    "expense",
                    "password",
                ],
            )
        )
    ):

        return make_result(
            intent="Unclear Request",
            decision="Ask Follow-up",
            response=(
                "I don't have enough information to determine the "
                "correct IT resolution. Please tell me which device, "
                "system, or application is affected and describe what "
                "happens when you try to use it."
            ),
            sources=[],
            confidence="Low",
            action="Collect additional information",
            needs_ticket=False,
            follow_up=(
                "Which device, system, or application is not working, "
                "and what error or behavior are you seeing?"
            ),
        )

    # ========================================================
    # 13. UNKNOWN / UNSUPPORTED REQUEST
    # ========================================================

    return make_result(
        intent="Unclassified Request",
        decision="Clarification / Human Review",
        response=(
            "I could not find enough information in the supplied "
            "Veridian Corp policies to safely resolve this request. "
            "I will not invent a policy or unsupported action. Please "
            "provide additional details or route the case for human "
            "review."
        ),
        sources=[],
        confidence="Low",
        action="Request clarification",
        needs_ticket=False,
        follow_up=(
            "What system is affected, what problem are you seeing, "
            "and is there an error message?"
        ),
    )


# ============================================================
# STRUCTURED TICKET GENERATOR
# ============================================================

def generate_ticket(message, result):
    """
    Generate a structured ticket for cases that require
    escalation, approval, diagnosis, or human handling.
    """

    ticket_id = "AI-" + str(uuid.uuid4())[:8].upper()

    decision_lower = result["decision"].lower()
    intent_lower = result["intent"].lower()

    if (
        "security" in intent_lower
        or result["assigned_to"] == "IT Security"
    ):
        status = "Escalated - Security"

    elif "review" in decision_lower:
        status = "Pending Human Review"

    elif "approval" in decision_lower:
        status = "Pending Approval"

    elif "manual" in decision_lower:
        status = "Assigned to IT"

    elif result["needs_ticket"]:
        status = "Open"

    else:
        status = "Resolved"

    return {
        "ticket_id": ticket_id,
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "issue": message,
        "intent": result["intent"],
        "decision": result["decision"],
        "confidence": result["confidence"],
        "priority": result["priority"],
        "assigned_to": result["assigned_to"],
        "action": result["action"],
        "status": status,
        "sources": result["sources"],
    }


# ============================================================
# SOURCE DETAILS
# ============================================================

def get_source_details(source_ids):
    """
    Returns the complete policy information for the sources
    used by the agent.
    """

    sources = []

    for source_id in source_ids:

        if source_id in KNOWLEDGE_BASE:

            source = KNOWLEDGE_BASE[source_id]

            sources.append(
                {
                    "id": source_id,
                    "title": source["title"],
                    "content": source["content"],
                }
            )

    return sources