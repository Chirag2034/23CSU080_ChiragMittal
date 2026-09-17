import json
import os
from datetime import datetime

import streamlit as st

from agent import analyze_request, generate_ticket, get_source_details
from knowledge_base import KNOWLEDGE_BASE
from data.data_pack import EMPLOYEE_REQUESTS, EXISTING_TICKETS


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Veridian IT Service Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATA FILES
# ============================================================

DATA_DIR = "data"
TICKET_FILE = os.path.join(DATA_DIR, "tickets.json")
AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.json")

os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path):
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def save_audit_log(
    message,
    result,
    ticket_id=None,
    request_id=None,
):
    logs = load_json(AUDIT_FILE)

    logs.append(
        {
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "request_id": request_id,
            "request": message,
            "intent": result["intent"],
            "decision": result["decision"],
            "confidence": result["confidence"],
            "action": result["action"],
            "priority": result["priority"],
            "sources": result["sources"],
            "ticket_id": ticket_id,
        }
    )

    save_json(AUDIT_FILE, logs)


def find_generated_ticket(request_id):
    """
    Prevent duplicate AI tickets for supplied REQ cases.
    """

    if not request_id:
        return None

    tickets = load_json(TICKET_FILE)

    for ticket in tickets:
        if ticket.get("request_id") == request_id:
            return ticket

    return None


def process_request(message, request_id=None):
    """
    Run the agent, create a ticket when required,
    and record the decision in the audit trail.
    """

    result = analyze_request(message)
    ticket = None

    if result["needs_ticket"]:

        existing = find_generated_ticket(request_id)

        if existing:
            ticket = existing

        else:
            ticket = generate_ticket(message, result)

            if request_id:
                ticket["request_id"] = request_id

            tickets = load_json(TICKET_FILE)
            tickets.append(ticket)
            save_json(TICKET_FILE, tickets)

    save_audit_log(
        message,
        result,
        ticket["ticket_id"] if ticket else None,
        request_id,
    )

    return result, ticket


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "latest_result": None,
    "latest_request": "",
    "latest_ticket": None,
    "selected_request_id": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.7rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-top: 3px;
        margin-bottom: 22px;
    }

    .request-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("Veridian Corp")
    st.caption("Internal IT Service Desk")

    st.divider()

    st.markdown("### Agent Capabilities")

    st.write("✓ Understand employee issues")
    st.write("✓ Retrieve relevant policies")
    st.write("✓ Ask sensible follow-ups")
    st.write("✓ Resolve routine requests")
    st.write("✓ Escalate risky cases")
    st.write("✓ Create structured tickets")
    st.write("✓ Show policy sources")
    st.write("✓ Maintain an audit trail")

    st.divider()

    st.markdown("### Guardrail")

    st.info(
        "The agent uses only the supplied Veridian Corp "
        "knowledge base. Unsupported decisions are not invented."
    )

    st.divider()

    st.caption("AIONOS — Assignment 2")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 Veridian IT Service Agent</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Policy-grounded employee support with transparent decisions, '
    'routing, ticketing and auditability.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================

(
    dashboard_tab,
    support_tab,
    requests_tab,
    tickets_tab,
    kb_tab,
    audit_tab,
) = st.tabs(
    [
        "🏠 Dashboard",
        "💬 AI Support Agent",
        "📥 Employee Requests",
        "🎫 Ticket Queue",
        "📚 Knowledge Base",
        "🧾 Audit Trail",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

with dashboard_tab:

    st.subheader("Service Desk Dashboard")

    st.write(
        "Operational overview of supplied employee requests, "
        "existing service tickets and AI-agent activity."
    )

    generated_tickets = load_json(TICKET_FILE)
    audit_logs = load_json(AUDIT_FILE)

    active_existing = [
        ticket
        for ticket in EXISTING_TICKETS
        if ticket["is_active"]
    ]

    closed_existing = [
        ticket
        for ticket in EXISTING_TICKETS
        if not ticket["is_active"]
    ]

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Employee Requests",
        len(EMPLOYEE_REQUESTS),
    )

    c2.metric(
        "Active Existing",
        len(active_existing),
    )

    c3.metric(
        "Historical Closed",
        len(closed_existing),
    )

    c4.metric(
        "AI Tickets",
        len(generated_tickets),
    )

    c5.metric(
        "Agent Decisions",
        len(audit_logs),
    )

    st.divider()

    st.markdown("### Assignment Data Overview")

    left, right = st.columns(2)

    with left:

        st.markdown("#### Employee Request Status")

        not_started = len(
            [
                r
                for r in EMPLOYEE_REQUESTS
                if r["initial_action"] == "Not started"
            ]
        )

        already_actioned = (
            len(EMPLOYEE_REQUESTS) - not_started
        )

        st.metric(
            "Not Started",
            not_started,
        )

        st.metric(
            "Already Partially Actioned",
            already_actioned,
        )

    with right:

        st.markdown("#### Existing Ticket Queue")

        st.metric(
            "Active Tickets Requiring Action",
            len(active_existing),
        )

        st.metric(
            "Closed Historical Tickets",
            len(closed_existing),
        )

    st.divider()

    st.markdown("### Agent Workflow")

    st.code(
        """
Employee Request
      ↓
Understand Intent
      ↓
Retrieve Relevant Policy
      ↓
Evaluate Policy + Risk
      ↓
 ┌──────────┬──────────────┬────────────┐
 │ Resolve  │ Ask Follow-up│ Escalate   │
 └──────────┴──────────────┴────────────┘
      ↓
Structured Ticket (when required)
      ↓
Audit Trail + Source Transparency
        """,
        language="text",
    )


# ============================================================
# AI SUPPORT AGENT
# ============================================================

with support_tab:

    st.subheader("Employee Support")

    st.write(
        "Enter an IT request. The agent will identify the issue, "
        "retrieve relevant policy information and determine the "
        "appropriate next action."
    )

    st.markdown("#### Quick Demo Scenarios")

    demo_scenario = st.selectbox(
        "Choose a scenario",
        [
            "Enter my own request",
            "Password / account lockout",
            "Expired VPN credentials",
            "Contractor VPN access",
            "Guest Wi-Fi",
            "Non-catalog software",
            "Printer problem",
            "Mailbox full",
            "Phishing email",
            "Work-from-home monitor",
            "Laptop replacement conflict",
            "Expense tool login",
            "Admin access request",
            "Unclear request",
        ],
        key="demo_selector",
    )

    examples = {
        "Enter my own request": "",
        "Password / account lockout":
            "I'm locked out of my account, tried my password 6 times.",
        "Expired VPN credentials":
            "My VPN stopped working this morning, says credentials expired.",
        "Contractor VPN access":
            "New contractor joining my team next week, they'll need VPN access.",
        "Guest Wi-Fi":
            "Can I get Wi-Fi access for a guest visiting our office tomorrow?",
        "Non-catalog software":
            "Need approval to install a data-analysis tool that's not in the software catalog.",
        "Printer problem":
            'Printer on the 3rd floor keeps showing "paper jam" even though there is no jam.',
        "Mailbox full":
            "My mailbox is full and I can't send emails.",
        "Phishing email":
            "I think I got a phishing email asking for my login — forwarding it to teammates.",
        "Work-from-home monitor":
            "I've started working from home 4 days a week, how do I get a monitor?",
        "Laptop replacement conflict":
            "My laptop won't turn on at all, it's completely dead, had it about 3.5 years now.",
        "Expense tool login":
            "I can't log into the expense tool, keeps saying invalid credentials.",
        "Admin access request":
            "Can someone give me admin access to the finance reporting server?",
        "Unclear request":
            "hey can you help, its not working",
    }

    employee_request = st.text_area(
        "Employee Request",
        value=examples[demo_scenario],
        height=130,
        key=f"custom_request_{demo_scenario}",
    )

    if st.button(
        "🔍 Analyze Request",
        type="primary",
        use_container_width=True,
        key="analyze_custom",
    ):

        if not employee_request.strip():

            st.warning(
                "Please enter an employee request."
            )

        else:

            result, ticket = process_request(
                employee_request
            )

            st.session_state.latest_result = result
            st.session_state.latest_request = employee_request
            st.session_state.latest_ticket = ticket

    if st.session_state.latest_result:

        result = st.session_state.latest_result
        ticket = st.session_state.latest_ticket

        st.divider()

        st.subheader("Agent Decision")

        c1, c2, c3, c4 = st.columns(4)

        c1.write("**Intent**")
        c1.write(result["intent"])

        c2.write("**Confidence**")
        c2.write(result["confidence"])

        c3.write("**Priority**")
        c3.write(result["priority"])

        c4.write("**Assigned To**")
        c4.write(result["assigned_to"])

        st.markdown(
            f"### Decision: {result['decision']}"
        )

        if result["priority"] == "Critical":
            st.error(result["response"])

        elif (
            "Escalate" in result["decision"]
            or "Review" in result["decision"]
            or "Conflict" in result["decision"]
        ):
            st.warning(result["response"])

        else:
            st.success(result["response"])

        st.markdown("#### Recommended Action")
        st.write(result["action"])

        if result.get("follow_up"):

            st.markdown("#### Follow-up Required")
            st.info(result["follow_up"])

        if ticket:

            st.markdown("#### Structured Ticket")

            t1, t2, t3 = st.columns(3)

            t1.metric(
                "Ticket ID",
                ticket["ticket_id"],
            )

            t2.metric(
                "Status",
                ticket["status"],
            )

            t3.metric(
                "Priority",
                ticket["priority"],
            )

        st.markdown("#### Sources Used")

        sources = get_source_details(
            result["sources"]
        )

        if sources:

            for source in sources:

                with st.expander(
                    f"{source['id']} — {source['title']}"
                ):
                    st.write(source["content"])

        else:

            st.warning(
                "No supplied policy directly supports an "
                "automatic resolution."
            )


# ============================================================
# EMPLOYEE REQUESTS
# ============================================================

with requests_tab:

    st.subheader("Supplied Employee Requests")

    st.write(
        "These are the 15 employee requests supplied in the "
        "assignment data pack."
    )

    request_options = {
        (
            f"{item['request_id']} — "
            f"{item['employee']} — "
            f"{item['request'][:60]}"
        ): item
        for item in EMPLOYEE_REQUESTS
    }

    selected_label = st.selectbox(
        "Select an employee request",
        list(request_options.keys()),
        key="employee_request_selector",
    )

    selected = request_options[selected_label]

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Request ID",
        selected["request_id"],
    )

    c2.write("**Employee**")
    c2.write(selected["employee"])

    c3.write("**Opened**")
    c3.write(selected["date_opened"])

    st.markdown("#### Employee Message")

    st.info(selected["request"])

    st.markdown("#### Initial Action in Supplied Data")

    st.write(selected["initial_action"])

    existing_ai_ticket = find_generated_ticket(
        selected["request_id"]
    )

    if existing_ai_ticket:

        st.success(
            "This supplied request has already been processed "
            f"and linked to {existing_ai_ticket['ticket_id']}."
        )

    if st.button(
        f"🤖 Analyze {selected['request_id']}",
        type="primary",
        use_container_width=True,
        key="analyze_supplied_request",
    ):

        result, ticket = process_request(
            selected["request"],
            selected["request_id"],
        )

        st.session_state.selected_request_id = (
            selected["request_id"]
        )

        st.session_state[
            "supplied_result"
        ] = result

        st.session_state[
            "supplied_ticket"
        ] = ticket

    if (
        st.session_state.get("selected_request_id")
        == selected["request_id"]
        and st.session_state.get("supplied_result")
    ):

        result = st.session_state.supplied_result
        ticket = st.session_state.get(
            "supplied_ticket"
        )

        st.divider()

        st.markdown(
            f"### Agent Analysis — {selected['request_id']}"
        )

        r1, r2, r3, r4 = st.columns(4)

        r1.write("**Intent**")
        r1.write(result["intent"])

        r2.write("**Decision**")
        r2.write(result["decision"])

        r3.write("**Priority**")
        r3.write(result["priority"])

        r4.write("**Confidence**")
        r4.write(result["confidence"])

        st.markdown("#### Agent Response")

        if result["priority"] == "Critical":
            st.error(result["response"])
        elif (
            "Escalate" in result["decision"]
            or "Review" in result["decision"]
            or "Conflict" in result["decision"]
        ):
            st.warning(result["response"])
        else:
            st.success(result["response"])

        st.markdown("#### Recommended Action")
        st.write(result["action"])

        if result.get("follow_up"):

            st.markdown("#### Follow-up Question")
            st.info(result["follow_up"])

        if ticket:

            st.markdown("#### Ticket")

            st.success(
                f"{ticket['ticket_id']} | "
                f"{ticket['status']} | "
                f"{ticket['assigned_to']}"
            )

        st.markdown("#### Evidence / Sources")

        source_details = get_source_details(
            result["sources"]
        )

        if source_details:

            for source in source_details:

                with st.expander(
                    f"{source['id']} — {source['title']}"
                ):
                    st.write(source["content"])

        else:

            st.warning(
                "No supplied policy supports automatic "
                "approval or resolution."
            )

    st.divider()

    st.markdown("### All 15 Requests")

    request_table = []

    for item in EMPLOYEE_REQUESTS:

        ai_ticket = find_generated_ticket(
            item["request_id"]
        )

        request_table.append(
            {
                "Request ID": item["request_id"],
                "Employee": item["employee"],
                "Opened": item["date_opened"],
                "Request": item["request"],
                "Initial Action": item["initial_action"],
                "AI Ticket": (
                    ai_ticket["ticket_id"]
                    if ai_ticket
                    else "Not generated"
                ),
            }
        )

    st.dataframe(
        request_table,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# TICKET QUEUE
# ============================================================

with tickets_tab:

    st.subheader("Ticket Queue")

    st.write(
        "Existing service-desk tickets are kept separate from "
        "tickets generated by this prototype."
    )

    existing_active = [
        ticket
        for ticket in EXISTING_TICKETS
        if ticket["is_active"]
    ]

    existing_closed = [
        ticket
        for ticket in EXISTING_TICKETS
        if not ticket["is_active"]
    ]

    generated = load_json(TICKET_FILE)

    t1, t2, t3 = st.columns(3)

    t1.metric(
        "Existing Active",
        len(existing_active),
    )

    t2.metric(
        "Historical Closed",
        len(existing_closed),
    )

    t3.metric(
        "AI Generated",
        len(generated),
    )

    st.divider()

    queue_section = st.radio(
        "View",
        [
            "Active Existing Tickets",
            "Historical Closed Tickets",
            "AI-Generated Tickets",
        ],
        horizontal=True,
    )

    if queue_section == "Active Existing Tickets":

        st.markdown(
            "### Active Tickets Requiring Resolution or Routing"
        )

        for ticket in existing_active:

            with st.expander(
                f"{ticket['ticket_id']} — "
                f"{ticket['issue_summary']}"
            ):

                st.write(
                    "**Employee:**",
                    ticket["employee"],
                )

                st.write(
                    "**Status:**",
                    ticket["status"],
                )

                analysis = analyze_request(
                    ticket["issue_summary"]
                )

                st.markdown(
                    "#### Agent Routing Recommendation"
                )

                st.write(
                    "**Intent:**",
                    analysis["intent"],
                )

                st.write(
                    "**Decision:**",
                    analysis["decision"],
                )

                st.write(
                    "**Action:**",
                    analysis["action"],
                )

                st.write(
                    "**Sources:**",
                    ", ".join(
                        analysis["sources"]
                    )
                    if analysis["sources"]
                    else "No direct policy",
                )

    elif queue_section == "Historical Closed Tickets":

        st.markdown(
            "### Historical Tickets"
        )

        st.caption(
            "Closed tickets are displayed as historical context "
            "and are not reopened automatically."
        )

        st.dataframe(
            [
                {
                    "Ticket ID": ticket["ticket_id"],
                    "Employee": ticket["employee"],
                    "Issue": ticket["issue_summary"],
                    "Status": ticket["status"],
                }
                for ticket in existing_closed
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.markdown(
            "### Tickets Generated by the AI Agent"
        )

        if not generated:

            st.info(
                "No AI-generated tickets yet."
            )

        else:

            for ticket in reversed(generated):

                request_reference = ticket.get(
                    "request_id",
                    "Custom Request",
                )

                with st.expander(
                    f"{ticket['ticket_id']} — "
                    f"{request_reference} — "
                    f"{ticket['intent']}"
                ):

                    c1, c2 = st.columns(2)

                    with c1:

                        st.write(
                            "**Created:**",
                            ticket["created_at"],
                        )

                        st.write(
                            "**Priority:**",
                            ticket["priority"],
                        )

                        st.write(
                            "**Assigned To:**",
                            ticket["assigned_to"],
                        )

                    with c2:

                        st.write(
                            "**Status:**",
                            ticket["status"],
                        )

                        st.write(
                            "**Decision:**",
                            ticket["decision"],
                        )

                        st.write(
                            "**Confidence:**",
                            ticket["confidence"],
                        )

                    st.write(
                        "**Issue:**",
                        ticket["issue"],
                    )

                    st.write(
                        "**Action:**",
                        ticket["action"],
                    )

                    st.write(
                        "**Sources:**",
                        ", ".join(
                            ticket["sources"]
                        )
                        if ticket["sources"]
                        else "No direct policy",
                    )


# ============================================================
# KNOWLEDGE BASE
# ============================================================

with kb_tab:

    st.subheader(
        "Veridian Corp Knowledge Base"
    )

    st.write(
        "The agent is grounded only in the supplied "
        "knowledge and policy sources."
    )

    search_policy = st.text_input(
        "Search policies",
        placeholder=(
            "Search password, VPN, laptop, "
            "security, mailbox..."
        ),
    )

    displayed = 0

    for policy_id, policy in KNOWLEDGE_BASE.items():

        searchable = (
            policy_id
            + " "
            + policy["title"]
            + " "
            + policy["content"]
        ).lower()

        if (
            not search_policy
            or search_policy.lower()
            in searchable
        ):

            displayed += 1

            with st.expander(
                f"{policy_id} — "
                f"{policy['title']}"
            ):

                st.write(
                    policy["content"]
                )

    if displayed == 0:

        st.warning(
            "No policy matched your search."
        )


# ============================================================
# AUDIT TRAIL
# ============================================================

with audit_tab:

    st.subheader("Agent Audit Trail")

    st.write(
        "Every analyzed request records the agent's "
        "decision, confidence, action, source and "
        "generated ticket."
    )

    logs = load_json(AUDIT_FILE)

    st.metric(
        "Recorded Agent Decisions",
        len(logs),
    )

    st.divider()

    if not logs:

        st.info(
            "No agent activity recorded yet."
        )

    else:

        for log in reversed(logs):

            request_ref = log.get(
                "request_id"
            )

            title = (
                f"{log['timestamp']} | "
                f"{request_ref + ' | ' if request_ref else ''}"
                f"{log['intent']} | "
                f"{log['decision']}"
            )

            with st.expander(title):

                st.write(
                    "**Request ID:**",
                    request_ref
                    if request_ref
                    else "Custom Request",
                )

                st.write(
                    "**Employee Request:**",
                    log["request"],
                )

                st.write(
                    "**Intent:**",
                    log["intent"],
                )

                st.write(
                    "**Decision:**",
                    log["decision"],
                )

                st.write(
                    "**Confidence:**",
                    log["confidence"],
                )

                st.write(
                    "**Priority:**",
                    log["priority"],
                )

                st.write(
                    "**Action:**",
                    log["action"],
                )

                st.write(
                    "**Sources:**",
                    ", ".join(
                        log["sources"]
                    )
                    if log["sources"]
                    else "None",
                )

                st.write(
                    "**Generated Ticket:**",
                    log["ticket_id"]
                    if log["ticket_id"]
                    else "No ticket required",
                )