# AI-Powered DevOps Assistant (Free RAG Chatbot)

This is a beginner-friendly portfolio project that answers DevOps questions from runbooks and incident reports.

The original resume idea mentioned OpenAI API and AKS. Those can cost money, so this version uses free tools:

- FastAPI backend
- React frontend
- LangChain text splitting
- ChromaDB vector database
- Free local embeddings for retrieval
- Optional Ollama local LLM for GenAI answers
- Docker and Kubernetes manifests for portfolio/demo use

> Important: Do not claim you deployed to AKS unless you actually deploy to Azure AKS. For a free fresher project, say "containerized with Docker and included Kubernetes manifests."

## What You Will Build

The chatbot can answer questions like:

- "How do I troubleshoot CrashLoopBackOff?"
- "What should I check when API latency is high?"
- "What caused the payment API incident?"
- "How do I reduce database CPU saturation?"

The backend reads files from `data/runbooks` and `data/incidents`, splits them into chunks, stores them in ChromaDB, retrieves relevant chunks for a question, and then answers using either:

- Ollama local model, if installed
- A built-in retrieval fallback, if Ollama is not running

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── hash_embeddings.py
│   │   ├── main.py
│   │   ├── ollama.py
│   │   ├── rag.py
│   │   └── schemas.py
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   ├── incidents/
│   └── runbooks/
├── deployment/
│   └── k8s/
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Step 1: Open The Project Folder

In PowerShell:

```powershell
cd "C:\Users\gokul\Dropbox\My PC (LAPTOP-0IM7A3QK)\Documents\ChatBot_RAG"
```

## Step 2: Start The Backend

Create and activate a Python virtual environment:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the backend:

```powershell
python -m app.main
```

Backend URL:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Step 3: Index The Documents

Open a second PowerShell window and run:

```powershell
cd "C:\Users\gokul\Dropbox\My PC (LAPTOP-0IM7A3QK)\Documents\ChatBot_RAG"
Invoke-RestMethod -Method Post http://127.0.0.1:8000/ingest
```

Expected result:

```text
indexed_count : number of chunks indexed
```

Test one backend question:

```powershell
$body = @{
  question = "How do I troubleshoot CrashLoopBackOff in Kubernetes?"
  top_k = 4
} | ConvertTo-Json

Invoke-RestMethod -Method Post http://127.0.0.1:8000/chat -ContentType "application/json" -Body $body
```

## Step 4: Optional Free GenAI With Ollama

The project works without Ollama, but Ollama makes the answers more natural.

Install Ollama from:

```text
https://ollama.com/download
```

After installing, open PowerShell:

```powershell
ollama pull llama3.2:3b
ollama serve
```

If `ollama serve` says Ollama is already running, that is fine.

Then restart the backend and ask a question again. The API response will show:

```text
model_used : ollama:llama3.2:3b
```

If your laptop has low RAM, try a smaller model:

```powershell
ollama pull qwen2.5:1.5b
```

Then set the model before starting the backend:

```powershell
$env:OLLAMA_MODEL="qwen2.5:1.5b"
python -m app.main
```

## Step 5: Start The Frontend

Open another PowerShell window:

```powershell
cd "C:\Users\gokul\Dropbox\My PC (LAPTOP-0IM7A3QK)\Documents\ChatBot_RAG\frontend"
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

Open that URL in your browser and ask:

```text
What should I check when the payment API has high latency?
```

## Step 6: Useful Development Commands

Backend health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Re-index documents:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/ingest
```

Stop backend/frontend:

```text
Press Ctrl + C in the terminal where it is running.
```

Deactivate Python virtual environment:

```powershell
deactivate
```

## Step 7: Run With Docker

Docker Desktop is free for personal learning.

From the project root:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:5173
```

Stop Docker:

```powershell
docker compose down
```

## Step 8: Upload To GitHub

Create a new empty GitHub repository named:

```text
devops-rag-assistant
```

Do not add README, .gitignore, or license on GitHub because this project already has files.

From the project root:

```powershell
cd "C:\Users\gokul\Dropbox\My PC (LAPTOP-0IM7A3QK)\Documents\ChatBot_RAG"
git status
git add .
git commit -m "Initial DevOps RAG assistant"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/devops-rag-assistant.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Resume Bullet You Can Honestly Use

```text
AI-Powered DevOps Assistant (RAG Chatbot) | 2025
- Built a free local retrieval-augmented generation chatbot using FastAPI, React, LangChain text splitting, ChromaDB, and Ollama-compatible local LLMs to answer questions from DevOps runbooks and incident reports.
- Implemented document ingestion, vector search, source citations, Docker packaging, and Kubernetes manifests to simulate a production-style DevOps assistant for faster incident troubleshooting.
```

## How To Explain This In Interviews

Simple explanation:

```text
I built a RAG chatbot for DevOps knowledge. First, the backend loads runbooks and incident reports. Then it splits the text into smaller chunks using LangChain. Those chunks are stored in ChromaDB as vectors. When a user asks a question, the backend retrieves the most relevant chunks and sends them as context to a local LLM through Ollama. The frontend shows the answer and the source documents used.
```

Why this is free:

```text
Instead of paid OpenAI APIs, I used Ollama for local open-source models. Instead of paid AKS deployment, I added Docker and Kubernetes manifests that can run locally or be adapted later for cloud deployment.
```

