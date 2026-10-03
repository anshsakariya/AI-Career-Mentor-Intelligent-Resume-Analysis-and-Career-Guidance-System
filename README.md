# AI Career Mentor: Intelligent Resume Analysis & Career Guidance System

![Version](https://img.shields.io/badge/version-1.0.0-indigo)
![Framework](https://img.shields.io/badge/Framework-Django%204.2%2B-green)
![UI](https://img.shields.io/badge/UI-Bootstrap%205%20Dark-cyan)
![AI Architecture](https://img.shields.io/badge/Architecture-Multi--Agent%20System-blue)

A complete, production-ready **AI-Powered Career Mentor Web Application** built using **Django**, **Bootstrap 5**, **Scikit-learn**, **PyPDF2**, **NLTK**, and **Google Gemini API** with smart local fallback algorithms.

---

## 🌟 Key Features

1. **User Authentication & Career Profile Management**:
   - Secure Registration, Login, Logout, Profile update.
   - Comprehensive profile tracking (Education, Degree, University, Graduation Year, Experience Level, Target Role, Years of Experience, Career Objective).

2. **PDF Resume Text Extraction & NLP Skill Detection**:
   - Upload PDF resumes securely (validated for size <= 5MB and `.pdf` extension).
   - PyPDF2 text extraction service.
   - NLTK & database-driven Skill Dictionary for technical skill extraction.

3. **ATS Resume Scoring Engine**:
   - Calculates dynamic ATS Score from 0 to 100 based on weighted metrics:
     - Skills Match (25%)
     - Keyword Alignment for Target Role (25%)
     - Resume Structure & Section Completeness (15%)
     - Education (15%)
     - Experience History (10%)
     - Projects & Portfolio (10%)
   - Generates actionable strengths, weaknesses, and step-by-step improvement recommendations.

4. **ML Job Recommendation Engine**:
   - Benchmark database of realistic sample jobs.
   - Powered by **Scikit-learn TF-IDF Vectorization** and **Cosine Similarity** + Skill set overlap matching.
   - Ranks job postings with exact match percentages and provides matched vs. missing skill breakdowns.

5. **Skill Gap Analysis & Generative Learning Roadmap**:
   - Compares user's extracted skills against target career requirements to identify missing skills.
   - Generates personalized monthly and weekly learning curriculums (using Gemini API or rule-based fallback).
   - Interactive progress bar and milestone checklist with completion toggling.

6. **Agentic AI System (Multi-Agent Architecture)**:
   - **Resume Agent**: Inspects document structure, calculates ATS scores, suggests keyword improvements.
   - **Job Agent**: Analyzes job descriptions, computes similarity, explains job fit.
   - **Planner Agent**: Identifies skill gaps, synthesizes learning roadmaps, prioritizes tasks.
   - **Central Orchestrator**: Parses user natural language prompts and dispatches to specialized sub-agents or Gemini LLM.

7. **Interactive AI Career Chatbot**:
   - Persistent chat session stored in SQLite/PostgreSQL.
   - Context-aware answers based on live user resume metrics, roadmap progress, and career goals.

8. **Analytical Dashboard & Data Visualizations**:
   - Real-time aggregate metric cards.
   - Chart.js Doughnut chart (Mastered vs. Missing Skills) and Bar chart (ATS Category Breakdown).

9. **Django Admin Panel**:
   - Full administration management for Users, Profiles, Resumes, Resume Analyses, Skills, Jobs, Job Recommendations, Roadmaps, Roadmap Tasks, and Chat Conversations.

---

## 🏗️ Technology Stack

- **Backend**: Python 3.13+, Django 4.2+, Django REST Framework
- **Frontend**: HTML5, CSS3, Bootstrap 5 (Custom Dark Glassmorphic Theme), Vanilla JavaScript
- **Database**: SQLite3 (Local Dev) / PostgreSQL ready
- **AI / ML / Data Science**: Scikit-learn (TF-IDF & Cosine Similarity), Pandas, NumPy, NLTK, Google Gemini API (`google-generativeai`)
- **PDF Extraction**: PyPDF2
- **Data Visualization**: Chart.js

---

## 📁 Project Architecture

```text
ai_career_mentor/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── resumes/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── services.py
│   ├── urls.py
│   └── admin.py
│
├── jobs/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── urls.py
│   └── admin.py
│
├── skills/
│   ├── models.py
│   └── admin.py
│
├── recommendations/
│   ├── models.py
│   └── admin.py
│
├── roadmap/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── chatbot/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── agents/
│   ├── resume_agent.py
│   ├── job_agent.py
│   ├── planner_agent.py
│   └── orchestrator.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── accounts/
│   ├── resumes/
│   ├── jobs/
│   ├── roadmap/
│   └── chatbot/
│
├── static/
│   └── css/
│       └── styles.css
│
└── utils/
    ├── seed_db.py
    └── create_admin.py
```

---

## ⚡ Quick Start & Installation Commands

### 1. Virtual Environment Setup
```bash
# Clone repository
git clone https://github.com/your-username/ai-career-mentor.git
cd ai-career-mentor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and optionally set your Google Gemini API key:
```env
SECRET_KEY=django-insecure-ai-career-mentor-super-secret-key-2026!
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: If `GEMINI_API_KEY` is left blank, the application will seamlessly fall back to local rule-based and NLP algorithms).*

### 4. Database Setup & Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Skills & Sample Job Listings
```bash
python utils/seed_db.py
```

### 6. Create Admin Credentials
```bash
python utils/create_admin.py
```
- **Admin Username**: `admin`
- **Admin Password**: `adminpass123`

---

## 🚀 Running the Web Application

Start the local development server:
```bash
python manage.py runserver
```
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

Access the Django Admin Dashboard at:
```
http://127.0.0.1:8000/admin/
```

---

## 🧪 Running Automated Unit Tests

Run the test suite to verify authentication, PDF parsing, ATS scoring, ML job matching, and roadmap generation:
```bash
python manage.py test
```

---

## 🤖 Multi-Agent AI Workflow

```text
                     [ User Natural Language Prompt ]
                                    │
                                    ▼
                          [ Central Orchestrator ]
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
  [ Resume Agent ]           [ Job Agent ]             [ Planner Agent ]
  • PDF Extraction           • TF-IDF Vectorizer       • Skill Gap Matrix
  • ATS Scoring (0-100)      • Cosine Similarity       • 3-Month Roadmap
  • Keyword Feedback         • Skill Overlap Fit       • Milestone Progress
```

---

## 📄 License & Attribution

Developed as a Final MCA Capstone Project. Designed for academic and professional career guidance applications.
