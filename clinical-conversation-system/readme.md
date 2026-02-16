# 🏥 AI-Driven Clinical Conversation System
### B.Tech Project in AI and Data Science (Semester 6)

An advanced healthcare solution designed to automate the documentation of clinical encounters. This system transcribes doctor-patient audio, identifies speaker roles, extracts medical entities, and generates professional clinical summaries (SOAP notes).



---

## 🚀 Core Features
- **Speech-to-Text:** Powered by **OpenAI Whisper** for high-fidelity transcription.
- **Smart Diarization:** Heuristic logic to distinguish between **Doctor** and **Patient** voices.
- **Abstractive Summarization:** Uses the **BART-Large-CNN** Transformer to synthesize professional medical narratives.
- **Entity Extraction:** Automated identification of medications, symptoms, and medical conditions.
- **History Retrieval:** Symptom-based search across longitudinal patient records.

---

## 🛠️ Tech Stack
| Component | Technology |
| :--- | :--- |
| **Backend** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL |
| **STT Model** | OpenAI Whisper (Base) |
| **NLP Model** | Facebook BART-Large-CNN |
| **ORM** | SQLAlchemy |
| **Logging** | Loguru |

---
## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd clinical-conversation-system

## 2. Install Dependencies

Run the following command to install the necessary AI libraries, web framework, and database drivers.

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary whisper-openai torch transformers loguru python-multipart


## 3. PostgreSQL Database Configuration

### Create Database

Open **pgAdmin 4** or `psql` and execute:

```sql
CREATE DATABASE clinical_db;
### 🔑 Set User Password
In your terminal or query tool, execute the following to set your database password:
```sql
ALTER USER postgres WITH PASSWORD 'your_secure_password';
### 🔗 Update Connection String
Open `backend/config/database.py` and update the database connection URL:

```python
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:your_secure_password@localhost:5432/clinical_db"
# 🏃 Running the Application

## Start the FastAPI Server

Launch the backend using **uvicorn**.  
The `--reload` flag ensures the server restarts automatically when you make code changes.

```bash
uvicorn backend.app.services.main:app --reload
Once the server is running, access the interactive Swagger UI to test all endpoints  
(**Transcription, Summarization, History Retrieval**) directly from your browser:

**URL:** http://127.0.0.1:8000/docs

