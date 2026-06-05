# ResumeMind AI 🚀
An AI-powered, professional-grade Resume Parser and Applicant Tracking System (ATS) built with a Next.js (TypeScript) frontend and FastAPI (Python) backend. The platform integrates spaCy NLP, PyMuPDF parsing, and Firebase Firestore/Storage services to extract candidate profiles, evaluate match scores against job descriptions, and deliver actionable career insights.

---

## 🧭 Table of Contents
1. [AI Capabilities & Features](#-ai-capabilities--features)
2. [How the AI Matching Engine Works](#-how-the-ai-matching-engine-works)
3. [System Workflow](#-system-workflow)
4. [Project Directory Structure](#-project-directory-structure)
5. [Installation & Setup](#-installation--setup)
   - [Prerequisites](#prerequisites)
   - [Backend Setup](#backend-setup)
   - [Frontend Setup](#frontend-setup)
6. [API Documentation](#-api-documentation)
7. [Dashboards & Usage](#-dashboards--usage)
8. [Technologies Used](#-technologies-used)

---

## 🧠 AI Capabilities & Features

ResumeMind AI leverages advanced NLP pipeline processing to analyze resumes and match them against job requirements.

### 🌟 Core AI Features
- **ATS Resume Parsing**: Extracts structured meta-information from PDF uploads, including email addresses, phone numbers, education levels, years of experience, and technical skill sets.
- **Weighted ATS Matching**: Calculates a multi-dimensional match score between the candidate's resume and a specific job description.
- **Missing Skills Gap Analysis**: Identifies critical skills and qualifications requested in the job description that are missing from the applicant's resume.
- **Actionable Improvement Suggestions**: Generates targeted recommendations (e.g., adding metrics/KPIs, acquiring specific degrees/certifications, or integrating industry-specific keywords) to help candidates optimize their resumes.
- **Career Role Recommendation**: Maps the candidate's skills profile to specialized tech roles, such as:
  * Frontend Developer
  * Backend Developer
  * Machine Learning Engineer
  * DevOps Engineer
- **AI Recommendation fitment Paragraph**: Formulates automated, structured recruiter fitment feedback (e.g., *Highly Recommended*, *Consider for Interview*, *Not Recommended*) detailing why the applicant fits or lacks qualifications.

### 🔍 NLP Capabilities
- **Semantic Keyword Extraction**: Uses lemmatization (spaCy NLP pipeline) to process nouns and proper nouns, separating syntax variations (e.g., "developed", "developing", "developer" all map to the base lemma "develop").
- **Custom Skill Pattern Matching**: Leverages regex and vocabulary dictionary search across a large taxonomy of developer skills to categorize languages, tools, and frameworks.
- **Semantic Fallback Similarity**: If a job description contains no explicit nouns or skills, the system automatically falls back to spaCy's vector-based document similarity index to evaluate context fit.

---

## 📊 How the AI Matching Engine Works

The match score is calculated using a **weighted multi-criteria formula** to ensure a balanced evaluation:

$$\text{Overall Score} = (\text{Skills Score} \times 0.40) + (\text{Experience Score} \times 0.25) + (\text{Education Score} \times 0.15) + (\text{Keyword Score} \times 0.20)$$

### 1. Skills Match (40% Weight)
Compares the set of skills extracted from the job description ($S_{JD}$) and the resume ($S_{Resume}$):
$$\text{Skills Score} = \frac{|S_{JD} \cap S_{Resume}|}{|S_{JD}|} \times 100$$
*If no specific skills are found in the JD, it evaluates resume skill density up to a maximum of 100%.*

### 2. Experience Match (25% Weight)
Extracts years of experience from the resume and searches the JD for required experience (defaults to 2 years if none specified). 
- If $\text{Resume Years} \ge \text{JD Required Years}$, score is **100%**.
- Otherwise, it calculates a ratio: $\frac{\text{Resume Years}}{\text{JD Required Years}} \times 100$ (with a baseline minimum of **45%** if any experience is present).

### 3. Education Match (15% Weight)
Determines education levels of the applicant and compares it to the JD's minimum education criteria (PhD, Master's, Bachelor's, Associate's).
- Meeting or exceeding requirements yields **100%**.
- Being one level below yields **75%**.
- Anything lower yields **50%**.

### 4. Keyword Match (20% Weight)
Extracts nouns and proper nouns from the JD ($K_{JD}$) using spaCy and intersects them with all word lemmas from the resume ($L_{Resume}$):
$$\text{Keyword Score} = \frac{|K_{JD} \cap L_{Resume}|}{|K_{JD}|} \times 100$$

---

## 🔄 System Workflow

The end-to-end data pipeline is structured as follows:

```
[Candidate PDF Resume] ──> [PyMuPDF (Text Extraction)]
                                  │
                                  ▼
                    [spaCy NLP / Regular Expressions]
                    ┌───────────────────────────────┐
                    │ 1. Extract contact details    │
                    │ 2. Detect experience/education│
                    │ 3. Match skills / keywords    │
                    └─────────────┬─────────────────┘
                                  │
                                  ▼
                    [Weighted Scoring Evaluation]
                    ┌───────────────────────────────┐
                    │ - Skills (40%)                │
                    │ - Experience (25%)            │
                    │ - Education (15%)             │
                    │ - Keywords (20%)              │
                    └─────────────┬─────────────────┘
                                  │
                                  ▼
      ┌───────────────────────────┴───────────────────────────┐
      ▼                                                       ▼
[Firebase Storage & Firestore]                         [Web Frontend UI]
- Saves PDF file to Storage                            - Manager Dashboard (Shortlist/Reject)
- Saves metadata & scores to DB                        - Applicant Portal (Report Breakdowns)
```

---

## 📁 Project Directory Structure

```
ResumeParser/
├── backend/
│   ├── main.py                  # FastAPI Server Entry Point & Router
│   ├── ai_engine.py             # NLP parsing, matching, and scoring engine
│   ├── requirements.txt         # Python Backend Dependencies
│   ├── .env                     # Environment Configurations
│   ├── serviceAccountKey.json   # Firebase Admin Service SDK credentials
│   ├── uploads/                 # Local backup directory for uploaded PDFs
│   └── venv/                    # Local Python Virtual Environment
└── frontend/
    ├── src/app/
    │   ├── ThemeProvider.tsx    # Global Context Provider for Dark/Light Mode
    │   ├── globals.css          # Styling tokens, responsive grid systems, and components
    │   ├── page.tsx             # Manager Dashboard UI (main view)
    │   ├── applicant/
    │   │   └── page.tsx         # Applicant Portal UI
    │   └── utils/
    │       ├── api.ts           # Axios/Fetch integration endpoints
    │       └── firebase.ts      # Client-side Firebase configuration
    ├── package.json             # Frontend package configurations
    ├── tsconfig.json            # TypeScript configuration
    └── README.md                # Sub-readme for frontend development
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Firebase Project setup

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and Activate a Virtual Environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the spaCy NLP English Model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Set up Environment Variables:**
   Create a `.env` file in the `backend/` directory:
   ```env
   FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json
   FIREBASE_STORAGE_BUCKET=your-app-bucket-id.appspot.com
   ```
   *Make sure to download and place your Firebase `serviceAccountKey.json` credentials file inside the `backend/` directory.*

6. **Start the FastAPI Dev Server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Packages:**
   ```bash
   npm install
   ```

3. **Set up Environment Variables:**
   Create a `.env.local` file in the `frontend/` directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the Next.js Dev Server:**
   ```bash
   npm run dev
   ```

5. **Access the application:**
   Open [http://localhost:3000](http://localhost:3000) in your web browser.

---

## 🔌 API Documentation

FastAPI automatically generates documentation at `http://localhost:8000/docs`. The core endpoints include:

- **`GET /`** - Health check and welcome message.
- **`POST /api/upload`** - Extracts text from a PDF resume, parses its details, runs a baseline match, and stores the transaction metadata in Firestore.
- **`POST /api/match`** - Recomputes the weighted match score between an arbitrary resume and a specific job description.
- **`POST /api/storage/upload`** - Direct upload capability to Firebase Cloud Storage.
- **`GET /api/download/{filename}`** - Download parsed resumes stored on the backend.

---

## 🖥️ Dashboards & Usage

### 💼 Manager Dashboard (`/`)
Hiring managers can input or adjust the active job description in real-time, drag-and-drop multiple resume PDFs, and view an sorted leaderboard of candidates based on their AI Match score. From here, managers can view a comprehensive **AI report modal** containing:
- Scoring breakdowns
- Recommended career roles
- Improvement suggestions
- Recruiters can also update the candidate status (*Shortlist*, *Pending*, *Reject*).

### 👤 Applicant Portal (`/applicant`)
Designed as a self-service career tool, applicants can upload their resume to get immediate feedback. They receive an interactive **AI Report** showing where their resume ranks, what skills they are missing for typical engineering jobs, and precise suggestions on how to rewrite bullet points or add keywords to bypass ATS filters.

---

## 🛠️ Technologies Used

- **Frontend**: Next.js 15, React 19, TypeScript, Vanilla CSS (dynamic variables, dark/light theme support).
- **Backend**: FastAPI (Python), uvicorn.
- **AI/NLP**: spaCy (`en_core_web_sm` English pipelines), PyMuPDF (PDF text mining).
- **Database/Cloud**: Firebase Admin SDK (Cloud Firestore & Cloud Storage).