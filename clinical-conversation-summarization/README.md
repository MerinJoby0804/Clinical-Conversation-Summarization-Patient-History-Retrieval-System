## 🚀 Quick Start Guide (Team Setup)

Follow these steps to get the **Clinical Conversation Summarization & Patient History Retrieval System** running on your local machine.

### 1. Prerequisites
* **Python 3.10+**: [Download here](https://www.python.org/downloads/). 
  * **IMPORTANT**: During installation, you MUST check the box that says **"Add Python to PATH"**.
* **PostgreSQL**: [Download here](https://www.postgresql.org/download/).
  * Ensure the PostgreSQL server is running on your machine.
  * Use **pgAdmin** or the terminal to create a new database named `clinical_db`.

### 2. Installation
1. **Clone the Repository**:
   ```bash
   git clone <your-team-repo-link>
   cd clinical-conversation-system
   ### 2. Run the Setup Script
* **Double-click the `run.bat` file** in the project root.
* This script will automatically:
    * Create your virtual environment (`venv`).
    * Install all dependencies, including **OpenAI Whisper**, **FastAPI**, and your specified **NLP** libraries.
    * Generate a unique **SECRET_KEY** for your local instance to ensure security.

### 3. Database Configuration
Once the `run.bat` completes and creates your local `.env` file:
1. **Open the `.env` file** in a text editor (Notepad, VS Code, or PyCharm).
2. **Find the `DATABASE_URL` line** and update it with your local PostgreSQL credentials:
   ```text
   DATABASE_URL=postgresql://your_username:your_password@localhost:5432/clinical_db
   ### 3. Save & Launch
* **Save the `.env` file** and close your text editor.
* **Double-click the `run.bat`** again. Now that the environment and configuration are set, the script will launch the FastAPI server.

### 4. Verification
Once the server is running, you can access the interactive API documentation to test the summarization and retrieval features:

* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alt UI (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

> **⚠️ Note on First Run**: The very first time you start the server, it will download several hundred MBs of AI model weights (specifically **OpenAI Whisper** for transcription and **BART** for summarization). Please ensure you have a stable internet connection and do not close the terminal until the "Uvicorn running on..." message appears.
