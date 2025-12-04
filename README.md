# LogPilot — AI Log Incident Analyzer

LogPilot is an AI-powered troubleshooting assistant that analyzes raw logs (Java, Python, Kubernetes, Docker, Airflow, CI/CD) to automatically extract errors, identify root causes, and provide actionable quick fixes and long-term prevention.

Built with Python, Streamlit, Gemini 2.5, and a modular multi-agent log analysis pipeline.

---

## Features

- AI Log Analysis (Upload or Paste Logs)
  - Log type classification
  - Severity summary
  - Error segment extraction
  - Root cause analysis (RCA)
  - Quick fixes + long-term prevention suggestions

- Multi-Agent LLM Architecture
  - Log Type Detector Agent
  - Log Segmenter & Error Extractor Agent
  - Root Cause Analyst Agent
  - Fix Recommendation Agent
  - Knowledge Memory Agent (stores + matches past incidents)

- Memory Engine
  - Stores previous log incidents
  - Matches similar future errors to provide instant suggestions

- Streamlit Web UI
  - Upload log files
  - Paste input text
  - View output across 4 structured tabs

- AWS EC2 Deployable
  - Lightweight
  - No database required
  - API keys stored securely via .env

---

## Tech Stack

### Core
- Python 3
- Streamlit UI
- Gemini 2.5 Flash / Pro LLM
- Multi-Agent Pipeline (custom)

### Libraries
- Pydantic
- Python-dotenv
- Pathlib
- Streamlit
- tqdm

### Deployment
- Ubuntu EC2 (AWS)
- Port 8501 exposed externally
- Optional: Nginx reverse proxy

---

## Project Structure
```
logpilot/
├── src/
│   ├── agents/
│   │   ├── log_type_detector.py
│   │   ├── segmenter_cluster.py
│   │   ├── root_cause_analyst.py
│   │   ├── fix_recommender.py
│   │   └── knowledge_memory_agent.py
│   ├── tools/
│   │   └── file_read_tool.py
│   ├── pipeline.py
│   └── __init__.py
│
├── examples/
│   ├── java_error.log
│   └── k8s_crashloop.log
│
├── assets/
│   └── screenshots/
│       ├── logpilot_home.png
│       ├── logpilot_upload.png
│       └── logpilot_analysis.png
│
├── streamlit_app.py
├── requirements.txt
├── .gitignore
├── README.md
```
---
##  Local Setup (Start Here)

### 🔹 1. Clone the Repository
```bash
git clone https://github.com/keshvi-k/logpilot.git
cd logpilot
```
### 🔹 2. Create Virtual Environment
```bash
python3 -m venv venv
```
### 🔹 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 🔹 4. Add API Key (Gemini / Google Generative AI)
Create .env:

```bash
nano .env
```
ADD:
```bash
GEMINI_API_KEY=your_api_key_here
```
### 🔹 5. Run logPilot (Streamlit UI)
```bash
streamlit run streamlit_app.py
```
### App runs at:
```arduino
http://localhost:8501
```
### Running the Pipeline (CLI)
For example:
```bash
python -m src.pipeline
```
---

#  AWS EC2 Deployment (Ubuntu)

Follow these steps to deploy LogPilot in a production-like environment using AWS EC2.

## 🔹 1. Launch EC2 Instance
- Choose **Ubuntu 22.04 LTS**
- Instance type: **t2.micro** or **t3.small**
- Configure security group:
  - **Port 22** → SSH access
  - **Port 8501** → Streamlit UI access
  - (Optional) **Port 80** if later using Nginx

Download your `.pem` key and store it safely (outside the GitHub repo).

---

## 🔹 2. SSH Into the EC2 Instance
```bash
ssh -i "logpilot-key.pem" ubuntu@<EC2_PUBLIC_IP>
```
## 🔹 4. Clone LogPilot Repository
```bash
git clone https://github.com/keshvi-k/logpilot.git
cd logpilot
```
## 🔹 5. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## 🔹 6. Add API Key on EC2
Create .env:
```bash
nano .env
```
Add:
```ini
GEMINI_API_KEY=your_api_key_here
```
Save → CTRL+O → Enter → CTRL+X.
## 🔹 7. Run Streamlit App on EC2
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
```
Now open the app in your browser
``` cpp
http://<EC2_PUBLIC_IP>:8501

```
# Updating EC2 Deployment (After You Push New Code)

Whenever you update your code on your laptop:

Step 1 — Push changes to GitHub
```bash
git add .
git commit -m "Update Streamlit UI and improve analysis pipeline"
git push
```
Step 2 — Pull updates on EC2
```bash
ssh -i "logpilot-key.pem" ubuntu@<EC2_PUBLIC_IP>
cd logpilot
source venv/bin/activate
git pull origin main
```
Step 3 — Restart Streamlit

List running process:
```bash
ps aux | grep streamlit
```
Kill old instance:
```bash
kill <PID>
```

Start again:
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
```
# Sample Output (AI-Generated RCA)
```json
{
  "log_type": "JAVA",
  "primary_root_cause": "Database connection timed out due to socket read failure.",
  "symptoms": [
    "SQLException: Connection timed out",
    "SocketTimeoutException: Read timed out"
  ],
  "quick_fixes": [
    "Increase JDBC read timeout temporarily",
    "Restart the application instance to clear stale connections"
  ],
  "long_term_fixes": [
    "Monitor database connection pool usage",
    "Optimize long-running SQL queries",
    "Scale database CPU/Memory resources",
    "Add retry logic with exponential backoff"
  ]
}
```
# Roadmap

Future improvements planned for LogPilot:

- Multi-log comparison dashboard

- Kubernetes-specific crash analyzer

- Airflow DAG failure auto-analysis

- Slack / Teams real-time integration

- Docker container deployment

- Full REST API version using FastAPI

- Real-time log streaming via WebSockets
# Contributing

Pull requests and feature enhancements are welcome.
Open an issue for discussions or ideas.
