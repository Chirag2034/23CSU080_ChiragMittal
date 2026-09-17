# 🤖 Veridian IT Service Agent

**AIONOS Agentic AI Factory — Assignment 2: Internal Service Agent**

The **Veridian IT Service Agent** is a policy-grounded internal IT support prototype designed to assist employees with common IT service requests.

The agent understands employee issues, retrieves relevant policies from the supplied Veridian knowledge base, asks follow-up questions when required, resolves routine requests, escalates risky or unsupported cases, generates structured tickets, displays policy evidence, and maintains an audit trail of its decisions.

---

## 🎯 Project Objective

The objective of this project is to build a working internal employee-support agent for the IT function.

The solution demonstrates how an agent can convert unstructured employee IT requests into transparent and actionable service decisions while remaining grounded in supplied organizational policies.

---

## ✨ Key Features

- Employee IT request analysis
- Intent and issue identification
- Policy and knowledge-base retrieval
- Policy-grounded decision making
- Self-service resolution
- Troubleshooting recommendations
- Sensible follow-up questions
- Approval requirement detection
- Security escalation
- Human review for unclear or unsupported requests
- Policy conflict detection
- Structured IT ticket generation
- Priority and confidence classification
- Team routing
- Policy source/evidence display
- Complete audit trail

---

## 🏗️ Complete Solution Architecture

The solution follows the following architecture:

```text
Employee
   ↓
Streamlit User Interface
   ↓
Veridian IT Service Agent
   ↓
Intent / Issue Detection
   ↓
Knowledge Base & Policy Retrieval
   ↓
Policy-Grounded Decision Engine
   ↓
┌─────────────────────────────────────────────┐
│                                             │
│  Resolve       Ask Follow-up       Escalate │
│                                             │
└─────────────────────────────────────────────┘
   ↓
Structured Ticket Generation
(when human action is required)
   ↓
Audit Trail
   ↓
Final Response + Action + Source + Ticket
```

### Architecture Layers

**Presentation Layer**
- Streamlit user interface

**Agent / Decision Layer**
- Intent detection
- Policy retrieval
- Decision logic
- Guardrails

**Knowledge Layer**
- Veridian knowledge base
- Organizational policies
- Employee request data
- Existing ticket data

**Action Layer**
- Self-service resolution
- Troubleshooting
- Follow-up questions
- Escalation
- Ticket generation

**Governance & Traceability Layer**
- Policy evidence
- Confidence
- Priority
- Routing
- Audit trail

---

## 🔄 Process Flow

```text
Employee Request
       ↓
Understand the Issue
       ↓
Identify Intent
       ↓
Retrieve Relevant Policy
       ↓
Is Enough Information Available?
       ↓
 ┌─────┴─────┐
 No           Yes
 ↓             ↓
Ask           Evaluate Policy,
Follow-up     Risk & Authority
 ↓             ↓
Re-analyze    Select Action
               ↓
       ┌───────┼─────────┐
       ↓       ↓         ↓
    Resolve  Approval  Escalate
       │       │         │
       └───────┴─────────┘
               ↓
       Generate Ticket
       (when required)
               ↓
         Record Audit
               ↓
     Return Final Response
```

---

## 📥 Inputs

The agent works with the following inputs:

- 15 supplied employee requests (`REQ-01` to `REQ-15`)
- Existing IT service tickets
- Employee request status
- Previously actioned request information
- Employee responses to follow-up questions
- Custom employee IT requests entered through the interface

---

## 📚 Knowledge & Policy Sources

The agent is grounded in the supplied Veridian Corp knowledge and policy sources.

Examples include:

- **KB-01** — Password Reset
- **KB-02** — VPN Access
- **KB-03** — Laptop Replacement
- **KB-04** — Software Installation Requests
- **KB-05** — Printer Troubleshooting
- **KB-06** — Email Mailbox Quota
- **KB-07** — Guest Wi-Fi Access
- **KB-09** — Security Incident Reporting
- **KB-10** — Work-From-Home Equipment
- **Asset Management Policy**

The application does not intentionally create unsupported policy rules when the supplied sources do not provide sufficient authority.

---

## 🛡️ Assumptions and Guardrails

The following assumptions and guardrails are used:

- Supplied Veridian policies are treated as the authoritative source for this prototype.
- The agent does not invent missing organizational policies.
- Missing information results in a follow-up question.
- Conflicting policies result in human review.
- Security-sensitive requests are escalated.
- Requests requiring approval are routed appropriately.
- Unsupported privileged-access decisions are escalated for authorization review.
- Historical closed tickets are treated as historical information.
- Structured tickets are generated when human action, approval, or escalation is required.
- Policy evidence is displayed to make decisions transparent.

---

## 🧠 How the Agent Works

For each employee request, the agent performs the following steps:

1. Receives the employee's IT request.
2. Identifies the likely intent or issue.
3. Retrieves the relevant supplied policy or knowledge-base article.
4. Determines whether sufficient information is available.
5. Asks a follow-up question when necessary.
6. Evaluates policy requirements and risk.
7. Determines the appropriate action.
8. Resolves, troubleshoots, routes, or escalates the request.
9. Generates a structured ticket when required.
10. Records the decision and supporting evidence in the audit trail.

---

## 🎫 Ticket Generation

The application maintains three ticket categories:

- **Active Existing Tickets**
- **Historical Closed Tickets**
- **AI-Generated Tickets**

AI-generated tickets can contain information such as:

- Ticket ID
- Request ID
- Issue / Intent
- Priority
- Assigned Team
- Status
- Recommended Action

Tickets are generated for cases requiring human intervention, approval, escalation, or additional IT action.

---

## 📋 Audit Trail

The application maintains an audit trail for agent decisions.

Audit information can include:

- Request ID
- Employee Request
- Intent
- Decision
- Confidence
- Priority
- Recommended Action
- Policy Sources
- Generated Ticket ID

This provides traceability from the original employee request to the final agent decision.

Example:

```text
Employee Request
      ↓
Agent Decision
      ↓
Policy Evidence
      ↓
Escalation / Ticket
      ↓
Audit Record
```

---

## 🧪 Testing

The solution was tested using all **15 supplied employee requests (REQ-01 to REQ-15)**.

Representative test scenarios include:

| Request | Scenario | Agent Behaviour |
|---|---|---|
| REQ-01 | Laptop hardware failure | Policy conflict → Human review |
| REQ-02 | Guest Wi-Fi | Self-service resolution |
| REQ-03 | Account lockout | Manual IT unlock |
| REQ-04 | Software installation | Follow-up → IT Security review |
| REQ-06 | Printer problem | Troubleshooting |
| REQ-07 | WFH equipment | Approval workflow |
| REQ-08 | Phishing incident | Critical Security escalation |
| REQ-10 | Privileged access | Escalation due to missing authority |
| REQ-11 | Contractor VPN | Manager approval |
| REQ-13 | Laptop hardware issue | Hardware diagnosis |
| REQ-15 | Unclear request | Follow-up question |

### Important Guardrail Test

`REQ-10` demonstrates that the agent does not automatically approve a privileged-access request when no supplied policy provides authority to do so.

Instead, the request is escalated for human authorization review.

---

## 🚨 Example — Security Incident

For `REQ-08`, the employee reports a suspected phishing email.

The agent:

1. Identifies the request as a **Security Incident**.
2. Assigns **Critical** priority.
3. Retrieves **KB-09 — Security Incident Reporting**.
4. Recommends immediate Security escalation.
5. Advises against forwarding suspected phishing content to other employees.
6. Generates a structured Security ticket.
7. Records the complete decision in the audit trail.

This demonstrates end-to-end:

```text
Request → Intent → Policy → Decision → Escalation → Ticket → Audit
```

---

## 🛠️ Technology Stack

| Technology | Usage |
|---|---|
| Python | Core application and agent logic |
| Streamlit | Interactive web interface |
| JSON | Ticket and audit data storage |
| Git | Version control |
| GitHub | Project repository and submission |

---

## 🤖 AI Tools Used

### ChatGPT

ChatGPT was used as a **development assistant** during the project.

It assisted with:

- Planning the agent workflow
- Structuring the solution
- Development support
- Debugging and code refinement
- Test-case analysis
- Documentation preparation
- Presentation preparation

The final application remains grounded in the supplied Veridian knowledge and policy sources.

---

## 📁 Project Structure

```text
23CSU080_ChiragMittal/
│
├── app.py
├── agent.py
├── knowledge_base.py
├── requirements.txt
├── README.md
│
└── data/
    ├── data_pack.py
    ├── tickets.json
    └── audit_log.json
```

### File Description

- `app.py` — Streamlit application and user interface
- `agent.py` — Agent analysis and decision logic
- `knowledge_base.py` — Veridian policy / knowledge-base handling
- `data/data_pack.py` — Supplied assignment data
- `data/tickets.json` — Ticket information
- `data/audit_log.json` — Agent decision audit records
- `requirements.txt` — Python dependencies

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

### 2. Open the project directory

```bash
cd 23CSU080_ChiragMittal
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

After activating the virtual environment, run:

```bash
streamlit run app.py
```

The application will normally open at:

```text
http://localhost:8501
```

---

## 🖥️ Application Modules

The application provides the following main sections:

### Dashboard
Overview of employee requests, existing tickets, AI-generated tickets and agent decisions.

### AI Support Agent
Analyzes employee IT requests and generates policy-grounded decisions.

### Employee Requests
Displays supplied employee support requests.

### Ticket Queue
Displays active, historical and AI-generated tickets.

### Knowledge Base
Displays the supplied Veridian knowledge and policy sources.

### Audit Trail
Provides traceability for agent decisions.

---

## 📸 Screenshots

Screenshots of the working application can be added here, including:

- Dashboard
- AI Support Agent
- Security Incident Escalation
- Ticket Queue
- Knowledge Base
- Audit Trail

---

## 🎥 Demo Video

Open-access demo video:

**[Add Google Drive Demo Video Link Here]**

---

## 🔗 GitHub Repository

**[Add Final GitHub Repository Link Here]**

---

## 👨‍💻 Author

**Chirag Mittal**  
**Roll No.: 23CSU080**  
B.Tech CSE (AI & ML)

---

## 📌 Assignment

**AIONOS Agentic AI Factory**  
**Assignment 2 — Internal Service Agent**

**Project:** Veridian IT Service Agent