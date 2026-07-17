# ⚡ Aura-26: Stadium Pulse & Crowd Flow AI Assistant

**FIFA World Cup 2026 Stadium Operations & Crowd Management Solution**

---

## 🏟️ Executive Summary & Chosen Vertical
**Vertical:** **Crowd Management & Operational Intelligence**

**Aura-26 Stadium Pulse** is a context-aware, autonomous GenAI decision-support engine built for FIFA World Cup 2026 matchday operations. As stadiums like MetLife Stadium (NY/NJ), Azteca (Mexico City), and BC Place (Vancouver) prepare for unprecedented crowd densities of 80,000+ fans per venue, traditional static turnstile alerts and hardcoded crowd rules fail during sudden bottlenecks, extreme weather shifts, or emergency incidents.

Aura-26 replaces static rules with a **context-driven GenAI reasoning core** that dynamically synthesizes real-time crowd telemetry into multi-role, localized action plans.

---

## 🧠 Core GenAI Logic & Context-Awareness
Aura-26 does not act as a generic chatbot. Instead, it evaluates a high-dimensional **User & Environmental Context Vector** before synthesizing decisions:

1. **Temporal Context (`match_phase`):** 
   - *Pre-Match Ingress (-45m to Kickoff):* Focuses on turnstile load balancing and express gate redirection.
   - *Halftime Surge (+45m):* Prioritizes restroom concourse flows, concession line soothing, and stairwell safety.
   - *Post-Match Egress (+90m):* Coordinates transit hub metering, accessible shuttle departures, and crowd crush prevention.
2. **Spatial Context (`stadium_id`, `zone_id`, `gate_id`):** 
   - Precise concourse and sector tracking allows localized directives (e.g., *Level 2 North Concourse vs. VIP Gate B*).
3. **Role-Based Adaptation (`user_role`):**
   - **Operations Director:** Receives macro-level predictive surge alerts and staff deployment reallocation matrixes.
   - **Gate Supervisor / Steward:** Receives step-by-step turnstile rerouting protocols and crowd soothing tactics.
   - **Medical / Accessibility Officer:** Receives prioritized corridor clearance routing and emergency triage pathways.
4. **Telemetry Inputs (`crowd_density`, `weather_alert`, `incident_type`):**
   - Directly parses real-time sensor metrics (`crowd_density: 94%`) combined with dynamic alerts (`flash_rain_warning`, `turnstile_jam`).

### ⚙️ Structured GenAI Output
Using **Pydantic v2 validation and structured GenAI schema enforcement**, the AI guarantees deterministic payloads consisting of:
- `risk_assessment`: Severity level, bottleneck probability score, and primary root cause analysis.
- `action_plan`: Role-specific tactical steps with precise priority order.
- `digital_signage_payload`: Concise, high-impact text ready for instant push to concourse LED displays.
- `pa_broadcast_script`: Multilingual public address announcements (English, Spanish, French) calibrated for crowd tone, empathy, and urgency.

---

## 🏗️ Technical Architecture & Lightweight Stack
To comply strictly with the `< 10 MB` repository constraint and ensure zero-latency execution:
- **Backend:** **Python 3.11+ / FastAPI** (Async non-blocking REST API with automatic schema documentation).
- **Validation:** **Pydantic v2** (Enforces strict input/output contract sanitization).
- **AI Integration:** **Google GenAI SDK (`google-genai`)** utilizing structured output prompting.
- **Frontend Dashboard:** **Vanilla HTML5, Modern CSS (Design Tokens & Glassmorphism), and Async JavaScript** mounted cleanly via FastAPI static serving (No `node_modules`, zero build step bloat).
- **Testing:** **Pytest & Pytest-Asyncio** for robust unit testing of context parsing and AI decision synthesis.

---

## 🚀 Quick Setup & Installation

### Prerequisites
- Python 3.11 or higher installed.
- A valid Google Gemini API Key (`GEMINI_API_KEY`).

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository_url>
cd challenge4

# Create and activate virtual environment (blocked from git by .gitignore)
python3 -m venv .venv
source .venv/bin/activate

# Install lightweight dependencies
pip install -r requirements.txt
```

### 2. Configuration
Copy the `.env.example` file and insert your API key:
```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
```

### 3. Running the Server
Launch the async API server locally:
```bash
python3 -m app.main
# Or run via uvicorn directly:
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Once running, open your browser to **`http://localhost:8000`** to interact with the Aura-26 Stadium Pulse Operations Dashboard, or view interactive Swagger documentation at **`http://localhost:8000/docs`**.

---

## 📦 Project Structure (Attempt 1 Foundation)
```text
challenge4/
├── .env.example         # Clean credentials template
├── .gitignore           # Strict exclusion list (<10MB guarantee)
├── README.md            # Comprehensive project documentation
├── requirements.txt     # Lightweight Python dependencies
└── app/                 # Core backend & static serving
    ├── __init__.py
    ├── main.py          # FastAPI application initialization & routing
    ├── core/
    │   └── config.py    # Environment settings & application config
    ├── models/
    │   └── schemas.py   # Pydantic validation schemas for context & AI response
    ├── api/
    │   └── endpoints.py # REST endpoints for crowd intelligence & status
    ├── services/
    │   └── ai_service.py# GenAI core logic & structured reasoning engine
    └── static/          # Zero-dependency responsive UI
        ├── index.html   # Operations dashboard layout
        ├── styles.css   # Modern design tokens & accessibility styling
        └── app.js       # Async API client & UI state management
```

---

## ⚠️ Assumptions & Security Notes
- All API inputs are rigorously sanitized via Pydantic to prevent prompt injection and malformed telemetry.
- API keys are strictly loaded from environment variables (`.env`) and never stored in source code.
- Repository footprint is actively maintained under 1 MB through strict `.gitignore` rules and zero frontend binary builds.
