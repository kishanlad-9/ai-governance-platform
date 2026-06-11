# 🧠 AI Governance Platform

A structured, AI-powered platform that helps organisations discover, evaluate, and govern AI use cases — from problem definition through feasibility assessment to committee approval.

---

## What it does

Most organisations struggle to move from "we should use AI" to "here is a governed, prioritised list of AI opportunities." This platform solves that by providing a step-by-step workflow where business teams can submit AI use cases, get them automatically assessed for feasibility, and route them to a governance committee — all in one place.

---

## Modules

### ✅ Module 1 — Problem Definition
An AI analyst interviews the user through a natural conversation and extracts 8 structured fields from their responses:
- Business problem statement
- Business objective
- Proposed solution approach
- Timeline
- Action owner
- Workflow location
- Decision support required
- Quantified business value

The AI keeps asking follow-up questions until every field has a concrete answer. Once complete, the user reviews a summary table and submits — generating a unique reference ID (e.g. `GRP-20240601-143022`).

### ✅ Module 2 — Feasibility Assessment
The user selects a submitted problem and the AI automatically scores it across 5 dimensions — no manual sliders or human scoring required:

| Dimension | What it evaluates |
|---|---|
| 🤖 AI Suitability | Is the problem genuinely suited to AI vs rules/traditional ML? |
| 💰 Economic Viability | Does the claimed business value justify AI investment? |
| 🗄️ Data & Tech Readiness | How likely is adequate data and infrastructure to exist? |
| ⚙️ Workflow Maturity | Is the process stable enough to augment with AI? |
| 👥 Change Management | How likely is organisational adoption? |

Each dimension is scored 1–5. The overall average determines the verdict:
- **≥ 3.5** → Feasible
- **2.5 – 3.49** → Conditional
- **< 2.5** → Not Feasible

The AI also generates per-dimension reasoning, strengths, risks, and recommendations in a structured report.

### 🚧 Module 3 — Gain–Pain Analysis *(coming soon)*
Quantifies benefits, risks, and pain points for each approved use case using internal scoring formulas to produce a priority score.

### 🚧 Module 4 — Governance Dashboard *(coming soon)*
A central committee view to review all submissions, drill into assessments, approve or defer use cases, and monitor the AI opportunity pipeline.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend & hosting | Streamlit |
| AI | Google Gemini 2.5 Flash |
| Database | SQLite (local) |
| Language | Python 3.12 |

---

## Project structure

```
ai-governance-platform/
├── app.py                        # Entry point — run this
├── requirements.txt
├── .streamlit/
│   └── config.toml               # Theme and server settings
├── config/
│   ├── constants.py              # Field definitions, assessment dimensions, module list
│   ├── prompts.py                # All AI prompts — edit here to change AI behaviour
│   └── styles.py                 # All CSS in one place
├── database/
│   └── db.py                     # All SQLite operations
├── utils/
│   └── helpers.py                # API key resolution, AI calls, JSON parsing
└── modules/
    ├── sidebar.py                # Sidebar navigation
    ├── module1/
    │   └── chat.py               # Problem definition — conversation + summary + submit
    └── module2/
        └── select.py             # Feasibility — pick problem, AI assesses, results
```

---

## Run locally

**1. Clone**
```bash
git clone https://github.com/YOUR_USERNAME/ai-governance-platform.git
cd ai-governance-platform
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your Gemini API key**

Either set an environment variable:
```bash
export GEMINI_API_KEY=your-key-here      # Mac / Linux
set GEMINI_API_KEY=your-key-here         # Windows
```

Or create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-key-here"
```

Get a free key at [aistudio.google.com](https://aistudio.google.com).

**4. Run**
```bash
streamlit run app.py
```

App opens at `http://localhost:8501`.

---

## Deploy to Streamlit Cloud

1. Push this repo to GitHub (public repo or Streamlit Cloud connected account)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select repo → branch `main` → Main file path: `app.py`
4. Open **Advanced settings → Secrets** and add:
   ```
   GEMINI_API_KEY = "your-key-here"
   ```
5. Click **Deploy** — live in ~2 minutes

---

## Adding a new module

1. Create `modules/module3/` with your page file
2. Add the AI prompt to `config/prompts.py`
3. Add constants (if any) to `config/constants.py`
4. Unlock the module in the `MODULES` list in `config/constants.py` (change `"Locked"` to `"Active"`)
5. Add routing in `app.py`
6. Commit and push — Streamlit Cloud redeploys automatically

---

## Notes

- **Data persistence**: SQLite is file-based and local. On Streamlit Cloud, data resets on redeployment. For production, replace with a hosted database (Supabase, PostgreSQL, etc.) and set the `DB_PATH` environment variable.
- **API key security**: `.streamlit/secrets.toml` is in `.gitignore` and will never be committed. Always add your key through Streamlit Cloud's Secrets panel for deployed apps.
- **AI model**: Uses Gemini 2.5 Flash for both the Module 1 conversation and Module 2 assessment. Change the model name in `utils/helpers.py` if needed.
