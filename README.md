# 🏦 Agentic Rate Change Intelligence & Customer Retention System

> **EXL Hackathon 2026** · Built on EXL Agentic AI Sandbox · By Rohit Kankhedia

An enterprise-grade agentic AI system that identifies banking customers at risk of churning after a Fed rate change — and hands relationship managers a personalized, SOP-compliant retention playbook in under 3 minutes.

---

## 🚨 The Problem

Every Fed rate change triggers a silent crisis at banks:

- Customers quietly evaluate refinancing with competitors
- Relationship managers spend **2 days manually** building call lists
- By the time they act, customers are already pre-approved elsewhere
- A mid-size bank with $500M in auto loans loses **~$15M per rate cycle** to churn
- No intelligent prioritization. No personalized retention strategy.

---

## ✅ The Solution

**Rate Change Intelligence** — AI that does in 3 minutes what takes 2 days:

1. Ops team enters the Fed rate change (e.g. +25bps, effective June 20)
2. AI scans the entire loan portfolio and scores every customer on churn risk (0–100)
3. Generates a prioritized call list ranked by who is most likely to leave
4. Creates a personalized AI retention offer per customer — grounded in the bank's own SOP
5. Validates every offer against SOP compliance rules

**Business Impact:**
- 🔴 Identify top at-risk customers before they leave
- 💰 Recover $750K per rate event by retaining 50% of high-risk customers
- ⏱️ Save 2 days of manual work per rate change
- 📋 Every action grounded in and compliant with bank SOPs

---

## 🏗️ System Architecture

```
Fed Rate Change Announced
         │
         ▼
┌─────────────────────────┐
│   Rate Change Input     │  ← Ops team enters bps + effective date
└────────────┬────────────┘
             │
    ┌────────▼──────────┐
    │  Portfolio Risk   │  ← Scores 500+ customers on churn risk
    │  Scorer Agent     │    5 factors: rate gap, balance, months,
    └────────┬──────────┘    FICO, payment history
             │
    ┌────────▼──────────┐
    │  Competitor Gap   │  ← Compares bank rates vs 3 competitors
    │  Analyzer         │    Identifies dangerous rate gaps
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │  Retention Offer  │  ← Generates personalized offer per customer
    │  Generator Agent  │    Grounded in rate change SOP rules
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │  SOP Intelligence │  ← Operational Q&A for staff during execution
    │  Assistant        │    5 specialist agents, 5 SOP documents
    └───────────────────┘
             │
             ▼
  📊 Streamlit Dashboard
  Priority call list + personalized scripts + compliance checks
```

---

## 📊 Churn Risk Scoring Model

| Factor | Weight | Logic |
|---|---|---|
| Rate Gap vs Competitor | 35% | Higher gap = customer has more incentive to leave |
| Loan Balance | 25% | Larger balance = bigger monthly savings from refinancing |
| Months Remaining | 20% | More time left = more total savings possible |
| FICO Score | 15% | Better credit = more options at competitor banks |
| Payment History | 5% | Missed payments reduce ability to refinance elsewhere |

---

## 🖥️ Application Screens

| Tab | What you see |
|---|---|
| **Rate Change Intelligence** | Input rate change → KPI cards → risk charts → priority call list → AI retention offer per customer |
| **SOP Assistant** | Multi-agent chatbot answering operational questions from 5 bank SOPs |

---

## 📂 Project Structure

```
agentic-sop-assistant/
├── data/
│   ├── loan_portfolio.csv                      ← 500 synthetic customer records
│   ├── competitor_rates.csv                    ← Competitor rate table (3 banks)
│   ├── SOP_Bank_Rate_Change_Process.docx
│   ├── SOP_Loan_Origination_Underwriting.docx
│   ├── SOP_Wire_ACH_Payment_Processing.docx
│   ├── SOP_KYC_AML_Compliance.docx
│   └── SOP_Core_Banking_EOD_Processing.docx
├── agents/
│   ├── portfolio_risk_agent.py                 ← Churn scoring engine
│   ├── retention_offer_agent.py                ← Personalized offer generator
│   ├── router.py                               ← Question classifier
│   ├── guidance_agent.py                       ← Process & steps
│   ├── escalation_agent.py                     ← Contacts & escalation
│   ├── compliance_agent.py                     ← Regulatory compliance
│   ├── confidence_agent.py                     ← Answer quality scorer
│   ├── email_agent.py                          ← Email drafting
│   ├── multi_sop_agent.py                      ← Multi-SOP router
│   └── sop_watcher.py                          ← Auto-reload on SOP change
├── chatbot/
│   └── app.py                                  ← Streamlit dashboard (2 tabs)
├── scripts/
│   ├── generate_portfolio.py                   ← Generates synthetic loan data
│   ├── read_sop.py                             ← Extracts SOP text from Word docs
│   └── create_sops.py                          ← Generates all SOP Word documents
├── README.md
├── PITCH_SCRIPT.txt
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/RohitKankhedia/agentic-sop-assistant.git
cd agentic-sop-assistant
```

### 2. Install dependencies
```powershell
& C:\Users\vmuser\AppData\Local\Programs\Python\Python314\python.exe -m pip install python-docx groq streamlit pandas
```

### 3. Generate portfolio data
```powershell
& C:\Users\vmuser\AppData\Local\Programs\Python\Python314\python.exe scripts/generate_portfolio.py
```

### 4. Set your Groq API key
Get a free key at https://console.groq.com
```powershell
$env:GROQ_API_KEY = "gsk_your-key-here"
```

### 5. Run the app
```powershell
& C:\Users\vmuser\AppData\Local\Programs\Python\Python314\python.exe -m streamlit run chatbot/app.py
```

Open http://localhost:8501

---

## 💡 Demo Flow

1. Open **Tab 1 — Rate Change Intelligence**
2. Enter `25` in the rate change box (25 basis points = +0.25%)
3. Click **Run Churn Analysis**
4. See: how many customers are at risk, total at-risk balance, estimated loss
5. Browse the **priority call list** — download as CSV
6. Select a high-risk customer → click **Generate Retention Offer**
7. See AI-generated personalized offer with SOP compliance check
8. Switch to **Tab 2 — SOP Assistant** and ask: *"Who approves rate changes?"*

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM Inference | LLaMA 3.3 70B via Groq (free tier) |
| Churn Scoring | Python + Pandas (rule-based weighted model) |
| SOP Parsing | python-docx |
| Web Dashboard | Streamlit |
| Agent Orchestration | Custom Python multi-agent router |
| Data | Synthetic loan portfolio (500 customers, $132M balance) |

---

## 📈 Business Impact Summary

| Metric | Value |
|---|---|
| Portfolio scanned | 500 customers / $132M balance |
| Time to generate call list | < 3 minutes (vs 2 days manually) |
| Estimated loss per rate cycle (no action) | ~$15M on $500M portfolio |
| Recoverable with AI intervention | $750K–$4.5M per year |
| SOP documents loaded | 5 (Rate Change, Loan Origination, Wire/ACH, KYC/AML, EOD) |

---

## 🔮 Future Enhancements

- [ ] Live competitor rate feed via API
- [ ] Integration with core banking system (FiServ/Jack Henry) for real portfolio data
- [ ] CRM integration (Salesforce) to push call list directly to relationship managers
- [ ] Historical churn data to train a supervised ML model on top of the rule-based scorer
- [ ] Multi-bank deployment with bank-specific SOP and rate configuration
- [ ] Mobile app for relationship managers to access retention offers on the go

---

## 👤 Author

**Rohit Kankhedia**
EXL Hackathon 2026 · EXL Agentic AI Sandbox (Nuvepro)
GitHub: https://github.com/RohitKankhedia/agentic-sop-assistant
