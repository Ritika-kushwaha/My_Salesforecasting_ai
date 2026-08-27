

# ⚡ SalesGenie AI – AI Sales Assistant & Lead Intelligence Platform

SalesGenie AI is an enterprise-grade, multi-tenant B2B sales acceleration platform designed to automate end-to-end sales pipelines. Powered by **Google Gemini 2.5 Flash**, **FastAPI**, **PostgreSQL**, and **Streamlit**, SalesGenie transforms raw prospect data into actionable, high-velocity closed revenue through deep company intelligence, predictive qualification scoring, automated outreach copywriting, and real-time conversation intelligence.

---

## 🚀 Key Features & Modules

### 👥 Module 1: Lead Pipeline & Prospect Directory
* **Full CRUD Lead Management**: Add, view, edit, search, filter, and delete pipeline leads.
* **1-Click Pipeline Stage Advance**: Instantly transition leads across stages (`New`, `Contacted`, `Qualified`, `Proposal Sent`, `Closed Won`, `Closed Lost`).
* **Bulk CSV Import**: Import hundreds of prospects simultaneously with automatic data sanitization.
* **Executive PDF Brief Generator**: Generate and download formatted, client-ready PDF summaries on demand.

### 🏢 Module 2: Company Intelligence & Deep Research
* **Automated ICP Scoring**: Evaluate prospective companies against your Ideal Customer Profile (0–100 scale).
* **Gemini Market Dossiers**: Synthesize comprehensive overviews of business models, industry positioning, and market pain points.
* **Strategic Outreach Recommendations**: Receive tailored sales angles based on real-time market signals.

### ✉️ Module 3: AI Outreach & Cold Copy Generator
* **Multi-Channel Copy Generation**: Draft personalized Cold Emails, LinkedIn InMails, and Cold Call scripts.
* **Custom Tone & Value Props**: Align messaging with tones like *Professional & Persuasive*, *Urgent & Direct*, or *ROI-Driven*.
* **1-Click CRM Logging**: Automatically update prospect status to `Contacted` upon generating and sending copy.

### 🎯 Module 4: Predictive Lead Scoring & Qualification
* **Dynamic Qualification Engine**: Algorithmic scoring evaluating company size, industry vertical fit, and account engagement.
* **Tiered Strategic Playbooks**: Automated categorization into *Tier 1 (High Intent)*, *Tier 2 (Warm)*, and *Tier 3 (Nurture)* with prescriptive next steps.
* **Win Probability Projections**: Real-time conversion velocity forecasts.

### 🎙️ Module 5: Conversation Intelligence & Meeting Summarization
* **Transcript Analyzer**: Paste discovery call notes or meeting transcripts to automatically extract executive summaries, key discussion points, and next action items.
* **Automated Stage Sync**: Intelligent CRM stage recommendation directly synchronized to PostgreSQL.
* **Chronological Timeline**: Unified interaction feed tracking all touches across calls, emails, and meetings.

### 📊 Module 6: Executive Revenue Dashboard
* **Glassmorphic Cockpit**: Visual breakdown of total pipeline, qualified deal counts, conversion rates, and urgent touchpoints.
* **Pipeline Funnel Metrics**: Interactive distribution charts tracking deal velocity across each stage.

---

## 🛠️ Tech Stack

* **Backend**: FastAPI (Python 3.11+)
* **Database & ORM**: PostgreSQL, SQLAlchemy
* **AI Engine**: Google Gemini API (`gemini-2.5-flash`)
* **Frontend**: Streamlit (Modern Dark-Glass Design System)
* **Authentication**: Google OAuth 2.0 & Custom JWT/Session Authentication
* **Data & Export**: Pandas, ReportLab (PDF Generation)
* **Testing & Tools**: Postman, PyTest

---

## 📂 Project Structure

```text
salesgenie/
├── database/
│   ├── database.py         # SQLAlchemy engine & session setup
│   ├── main.py             # FastAPI backend application entry point
│   ├── models.py           # Database schemas (User, Lead, Company, Conversation)
│   └── routes.py           # REST API endpoints & Gemini integrations
├── modules/
│   ├── module1_leads.py    # Lead Pipeline & CRM management
│   ├── module2_company.py  # Company deep research & ICP analysis
│   ├── module3_outreach.py # Multi-channel AI copy generation
│   ├── module4_scoring.py  # Qualification engine & playbooks
│   ├── module5_conversation.py # Meeting intelligence & CRM sync
│   └── module6_dashboard.py # Executive metrics & pipeline analytics
├── login.py                # Google OAuth 2.0 & Work Email login
├── signup.py               # Workspace registration
├── main.py                 # Streamlit root application controller
├── requirements.txt        # Project dependencies
└── README.md               # Platform documentation

```

---

## ⚙️ Installation & Local Setup

### 1. Prerequisites

* Python 3.10+ installed
* PostgreSQL database instance running locally or on the cloud

### 2. Clone Repository & Setup Virtual Environment

```bash
git clone [https://github.com/your-username/salesgenie.git](https://github.com/your-username/salesgenie.git)
cd salesgenie

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/salesgenie

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
REDIRECT_URI=http://localhost:8501/

# API Backend Configuration
SALESGENIE_API_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)

```

---

## 🚀 Running the Platform

To run the complete platform, start both the FastAPI backend and Streamlit frontend in separate terminals:

### 1. Start the FastAPI Backend

```bash
uvicorn database.main:app --reload

```

* Backend will be live at: `http://127.0.0.1:8000`
* Interactive API Documentation (Swagger): `http://127.0.0.1:8000/docs`

### 2. Start the Streamlit Frontend

```bash
streamlit run main.py

```

* Frontend Application will be accessible at: `http://localhost:8501/`

---

## 🧪 Bulk Import Template

To test bulk importing in **Module 1 (Lead Pipeline)**, save the following as `sample_leads.csv` and upload it:

```csv
name,company,email,phone,industry,company_size,revenue,priority,status
Sarah Connor,Cyberdyne Systems,sarah.c@cyberdyne.io,+1 555-0143,Technology,500+,85000000,High,New
Marcus Vance,Vance Logistics Global,m.vance@vancelogistics.com,+1 555-0188,Retail,51-200,12500000,Medium,New
Elena Rostova,Apex BioHealth Technologies,elena@apexbiohealth.org,+1 555-0199,Healthcare,201-500,34000000,High,New
Devon Brooks,CloudScale Infrastructure,devon.b@cloudscale.net,+1 555-0122,Technology,51-200,6500000,Medium,New
Priya Sharma,FinEdge Financial Advisory,priya.s@finedgeadvisory.com,+1 555-0174,Finance,11-50,3200000,High,New

```
