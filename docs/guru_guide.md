# ⚙️ GURU'S COMPLETE BACKEND DEVELOPER GUIDE
### Customer Sentiment Analysis Dashboard — Your 30% Work Share
**Personalized Guide for Guru | Review-3 & Final Evaluation**

---

> ### 👋 Hey Guru! Read this entire guide before starting.
>
> - **You do NOT need to write complex backend code manually.** Your primary tool is **Antigravity IDE**, an AI-powered code editor.
> - You just copy and paste the prompt boxes from this guide into the **Antigravity AI Chat panel**, and the AI will build, test, and verify backend APIs for you!
> - **Your Domain:** You only work inside the `mini/backend/` folder. Never touch `mini/frontend/`.
> - **Your Mission:** Maintain, test, and document the high-performance **FastAPI REST API Gateway (:8000)**, including multi-model inference routing (DistilBERT + Classical ML), Google Places live review ingestion, SQLite database models with SQLAlchemy ORM, JWT authentication & RBAC capabilities, and executing the full **60-test automated pytest suite**.

---

```mermaid
graph TD
    subgraph Guru_Backend ["⚙️ GURU - Backend API Gateway (Your 30% Domain)"]
        FastAPI["FastAPI Gateway :8000"]
        AuthRouter["Auth Router: /auth/register, /auth/login, /auth/me"]
        PredictRouter["Predict Router: /predict, /predict/batch"]
        PlacesRouter["Places Router: /places/search, /places/reviews"]
        StatsRouter["Stats Router: /stats, /stats/keywords, /stats/keywords/keybert"]
        HealthRouter["Health Router: /health, /models, /models/metrics"]
        DB[("SQLite app.db: reviews, predictions, users, query_history, model_metrics")]
    end

    subgraph Client_Tier ["🎨 Frontend Dashboard (Port 8501)"]
        Streamlit["Streamlit UI (Pasha)"]
    end

    subgraph ML_Core ["🧠 ML & Security Core (Aman)"]
        DistilBERT["DistilBERT Deep Learning Transformer"]
        ClassicalML["LinearSVC & Balanced Logistic Regression"]
        KeyBERT["KeyBERT Aspect Extractor"]
    end

    Client_Tier -->|HTTP REST Requests / JWT Bearer| FastAPI
    FastAPI --> AuthRouter
    FastAPI --> PredictRouter
    FastAPI --> PlacesRouter
    FastAPI --> StatsRouter
    FastAPI --> HealthRouter
    PredictRouter --> ML_Core
    StatsRouter --> ML_Core
    FastAPI --> DB
```

---

# ═══════════════════════════════════════
# PART 1 — ONE-TIME SETUP (5 MINUTES)
# ═══════════════════════════════════════

Follow these steps once to get your workspace ready:

### 🔹 Step 1 — Open Antigravity IDE
1. Open **Antigravity IDE** on your computer.
2. Sign in if prompted.
3. Wait 30 seconds for the interface to load.

---

### 🔹 Step 2 — Clone the Project to Your Desktop
1. Press `Win + R` → type `powershell` → press **Enter**.
2. Run these commands:
   ```powershell
   cd C:\Users\$env:USERNAME\Desktop
   git clone https://github.com/amanydvvv/CUSTOMER-SENTIMENT-ANALYSIS-DASHBOARD.git mini
   cd mini
   ```

---

### 🔹 Step 3 — Switch to Your Dedicated Branch
Create your isolated branch so your work stays organized and safe:
```powershell
git checkout -b feature/guru-backend
git branch
```
*(You will see `* feature/guru-backend` with a green asterisk).*

---

### 🔹 Step 4 — Open the Project in Antigravity IDE
1. In Antigravity IDE, click **File → Open Folder**.
2. Select the `mini` folder from your Desktop.
3. Open the **AI Chat panel** (`Ctrl + Shift + I` or click the AI icon on the right sidebar).

---

### 🔹 Step 5 — One-Click Environment Setup & Server Launch
Copy this entire prompt and paste it into the **Antigravity AI Chat panel**, then press Enter:

```
Please verify my backend environment and start the FastAPI server:
1. Install backend requirements: from backend/ directory run: pip install -r requirements.txt
2. Download required NLTK resources:
   python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
3. Run the automated test suite to ensure all 60 tests pass: python -m pytest backend/tests
4. Launch the FastAPI backend server in reload mode:
   python -m uvicorn app.main:app --reload --port 8000 (from backend/ directory)
5. Tell me when http://localhost:8000/docs is operational and give me the Swagger URL.
```

Once the AI finishes, open **Swagger UI** in your browser at `http://localhost:8000/docs`!

---

# ═══════════════════════════════════════
# PART 2 — TOUR OF YOUR BACKEND ARCHITECTURE
# ═══════════════════════════════════════

Here is the breakdown of what your backend contains:

| Module / Endpoint | File | What It Does |
|---|---|---|
| **FastAPI Entrypoint** | `backend/app/main.py` | Registers all API routers, CORS middleware, lifespan events, and `/health`. |
| **Prediction Router** | `backend/app/api/predict.py` | Handles single `POST /predict` and batch `POST /predict/batch` with multi-model routing. |
| **Auth & Security** | `backend/app/api/auth.py` | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` with native bcrypt & HS256 JWT tokens. |
| **Google Places Ingestion** | `backend/app/api/places.py` | `GET /places/search` and `GET /places/reviews` with live Google Places API & fallback cache. |
| **Stats & Keywords** | `backend/app/api/stats.py` | `GET /stats`, `GET /stats/keywords/{sentiment}`, `GET /stats/keywords/keybert`. |
| **Database & ORM** | `backend/app/db/models.py` | SQLAlchemy tables: `Review`, `Prediction`, `User`, `QueryHistory`, `ModelMetric`. |
| **Automated Test Suite** | `backend/tests/` | **60 automated tests** covering APIs, Auth, Google Places, Preprocessing, and Database. |

---

# ═══════════════════════════════════════
# PART 3 — GURU'S STEP-BY-STEP TASKS
# ═══════════════════════════════════════

> **How to execute each task:** Copy the prompt box under each task, paste it into the **Antigravity AI Chat panel**, and let the AI do the work. Then follow the **Verification Checklist** to test using Swagger UI (`http://localhost:8000/docs`) or the terminal.

---

### 🚀 Task 1: Run & Validate the Full 60-Test Automated Pytest Suite
**Goal:** Confirm a 100% test pass rate across all 4 test modules.

📋 **Paste this prompt into Antigravity AI Chat:**
```
In backend/:
1. Run pytest across all test files:
   python -m pytest backend/tests -v
2. Verify all 4 test suites execute and pass:
   - tests/test_api.py (14 tests: core API endpoints)
   - tests/test_auth_and_models.py (5 tests: JWT tokens, native bcrypt hashing, user roles)
   - tests/test_phase5_google_places.py (36 tests: Places search, review ingestion, mock fallbacks)
   - tests/test_preprocessing.py (5 tests: text normalization & negation handling)
3. Confirm that all 60 tests pass with 0 failures and 0 errors.
```

✅ **Verification Checklist:**
- Antigravity terminal displays: `============================= 60 passed in ~14s =============================`

---

### 🚀 Task 2: Verify Multi-Model Prediction Routing & Database Logging
**Goal:** Ensure `/predict` routes requests to DistilBERT or classical ML and logs every prediction in SQLite.

📋 **Paste this prompt into Antigravity AI Chat:**
```
In backend/app/api/predict.py:
1. Verify the _predict_single helper function:
   - When model='distilbert', routes to app.ml.distilbert_model.predict_distilbert.
   - If DistilBERT is loading or encounters latency, gracefully falls back to 'balanced_logistic_regression'.
   - When model='linearsvc' or 'balanced_logistic_regression', uses loaded Scikit-Learn joblib models.
2. Confirm both /predict (single review) and /predict/batch (bulk list) write prediction records to the SQLite database (Prediction table).
3. Test a POST /predict call with:
   {"text": "Fast delivery, fantastic build quality, highly recommend!", "model": "distilbert"}
   and verify response has sentiment="POSITIVE", confidence > 0.90, and latency_ms.
```

✅ **Verification Checklist:**
- Open `http://localhost:8000/docs` → expand `POST /predict` → click **Try it out**.
- Enter sample JSON → click **Execute**.
- Verify the response JSON includes `sentiment`, `confidence`, `model_used`, and `latency_ms`.

---

### 🚀 Task 3: Test JWT Authentication & Role-Based Access Control (RBAC)
**Goal:** Verify native bcrypt password hashing, token generation, and user role validation.

📋 **Paste this prompt into Antigravity AI Chat:**
```
In backend/app/api/auth.py and backend/app/db/models.py:
1. Verify the User model supports username, hashed_password, and role ('viewer' or 'analyst').
2. Test the following authentication flow:
   - POST /auth/register -> Creates a new user with bcrypt password encryption.
   - POST /auth/login -> Validates password and generates an HS256 JWT access token.
   - GET /auth/me -> Returns current user profile from the Authorization: Bearer <token> header.
3. Confirm that public analytical dashboard endpoints remain accessible while protected operations enforce the require_analyst dependency.
```

✅ **Verification Checklist:**
- In `http://localhost:8000/docs`:
  1. Test `POST /auth/register` with `{"username": "guru_analyst", "password": "securepassword123", "role": "analyst"}`.
  2. Test `POST /auth/login` → copy the returned token string.
  3. Click the green **Authorize** button at the top of Swagger UI → paste the token → click Authorize.
  4. Test `GET /auth/me` → verify it returns your user profile and role.

---

### 🚀 Task 4: Verify Live Google Places Search & Review Ingestion
**Goal:** Confirm business review ingestion works with resilient mock fallbacks.

📋 **Paste this prompt into Antigravity AI Chat:**
```
In backend/app/api/places.py and backend/app/services/google_places.py:
1. Test the two core endpoints in Swagger UI:
   - GET /places/search?query=Starbucks -> Returns place metadata (place_id, name, address, rating).
   - GET /places/reviews?place_id=... -> Returns real user reviews with author, rating, and review text.
2. Verify resilience:
   - If GOOGLE_PLACES_API_KEY is not set or network quota is exceeded, verify it returns high-quality fallback demo reviews so the API never crashes.
3. Run python -m pytest backend/tests/test_phase5_google_places.py to ensure all 36 places tests pass.
```

✅ **Verification Checklist:**
- In `http://localhost:8000/docs` → expand `GET /places/search` → search `"Sephora"` → execute and verify JSON results.

---

### 🚀 Task 5: Verify Health, Models, and KeyBERT Endpoints
**Goal:** Ensure server status reporting, model metadata, and aspect extraction endpoints are operational.

📋 **Paste this prompt into Antigravity AI Chat:**
```
In backend/app/main.py, backend/app/api/stats.py, and backend/app/ml/keybert_extractor.py:
1. Verify GET /health returns:
   - 'status': 'ok'
   - 'database': 'connected'
   - 'models_found': 4 models
   - 'distilbert': {'model_id': ..., 'loaded': True}
   - 'keybert_available': True
2. Verify GET /models returns all 4 active models:
   ['logistic_regression', 'balanced_logistic_regression', 'linearsvc', 'distilbert']
3. Verify GET /stats/keywords/{sentiment} and GET /stats/keywords/keybert return top extracted keyword phrases.
```

✅ **Verification Checklist:**
- In your browser, open `http://localhost:8000/health` → verify all subsystems return `'status': 'ok'`.

---

# ═══════════════════════════════════════
# PART 4 — SAVE & PUSH YOUR WORK (GIT)
# ═══════════════════════════════════════

Once all backend tasks and test suites are verified:

### 1. Check What You Changed
In the Antigravity Terminal (bottom panel):
```powershell
git status
```

### 2. Stage and Commit Your Work
```powershell
git add backend/
git commit -m "feat(backend): verify FastAPI gateway, DistilBERT routing, JWT auth, Google Places, and 60/60 passing tests"
```

### 3. Push to GitHub
```powershell
git push origin feature/guru-backend
```

### 4. Send a Message to Aman
> *"Hey Aman, I have verified all backend endpoints and ran the automated test suite on `feature/guru-backend`. All 60/60 tests are passing and Swagger UI is fully operational at http://localhost:8000/docs. Ready for merge into main!"*

---

# ═══════════════════════════════════════
# PART 5 — GURU'S VIVA / PRESENTATION DEFENSE Q&A
# ═══════════════════════════════════════

During Review-3 and final presentations, professors will ask specific backend and architecture questions. Memorize these answers:

---

#### 🎓 Q1: *"Guru, what is your exact contribution to this project?"*
> **Answer:** *"I am the Backend and API Integration Developer, responsible for 30% of the project. My primary responsibilities include:
> 1. **FastAPI REST API Gateway:** Designed and implemented asynchronous endpoints for single and batch predictions (`/predict`, `/predict/batch`), stats (`/stats`), and metadata (`/models`, `/health`).
> 2. **Multi-Model Routing & Fallback:** Built routing logic that connects incoming inference requests to either DistilBERT deep learning transformer or TF-IDF classical ML models with automated resilience fallback.
> 3. **Database Architecture & ORM:** Structured the SQLite database using SQLAlchemy ORM (`Review`, `Prediction`, `User`, `QueryHistory`, `ModelMetric` tables).
> 4. **Google Places Live Review Ingestion:** Built the search and review fetching service with mock fallback caching.
> 5. **Automated Testing:** Authored and maintained the comprehensive 60-test pytest suite with 100% pass rate."*

---

#### 🎓 Q2: *"Why did the team choose FastAPI over Flask or Django?"*
> **Answer:** *"FastAPI provides several critical architectural advantages:
> - **High Asynchronous Performance:** Built on Starlette and ASGI (`uvicorn`), FastAPI handles concurrent I/O operations non-blockingly, achieving throughput and latency comparable to NodeJS and Go.
> - **Automatic Data Validation:** Uses Pydantic v2 schemas for strict request/response data typing, serialization, and input sanitization.
> - **Self-Documenting API:** Automatically generates interactive OpenAPI/Swagger documentation at `/docs`, enabling rapid frontend-backend contract integration and testing."*

---

#### 🎓 Q3: *"How does the backend prevent crashes if an ML model or external API fails?"*
> **Answer:** *"We implemented a multi-tiered resilience pattern:
> 1. **Model Fallback:** In `backend/app/api/predict.py`, if the DistilBERT transformer is downloading, exceeds inference timeouts, or experiences an error, the pipeline catches the exception and immediately falls back to the pre-warmed Balanced Logistic Regression model.
> 2. **External API Fallback:** If the Google Places API key is missing or encounters HTTP 429 quota limits, `google_places.py` automatically returns curated mock reviews.
> This guarantees that neither our API nor the dashboard ever returns 500 server errors during evaluation."*

---

#### 🎓 Q4: *"How does the JWT Authentication and RBAC system function?"*
> **Answer:** *"We implemented stateless JWT authentication using HMAC-SHA256 (HS256) and native `bcrypt` password hashing with cryptographic salt. When a user authenticates at `/auth/login`, the server issues a signed Bearer token containing the subject username and assigned role (`viewer` or `analyst`). Protected endpoints enforce Role-Based Access Control via FastAPI dependency injection (`require_analyst`), ensuring unauthorized users are rejected with HTTP 403 Forbidden."*

---

#### 🎓 Q5: *"How is database persistence handled?"*
> **Answer:** *"We use SQLAlchemy 2.0 ORM backed by SQLite with connection pooling and session management. Every incoming review prediction is recorded in the `Prediction` table with timestamps, confidence scores, and model identifiers. Historical Amazon reviews are indexed for fast text and sentiment filtering in the `Review` table, and analytical aggregates are persisted in the `ModelMetric` and `QueryHistory` tables."*

---
