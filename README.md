# 🤖 Local AI DevOps Reviewer

**A fully local, privacy-safe AI-powered DevSecOps code & infrastructure reviewer** — built with Streamlit, Ollama, PostgreSQL, and Docker Compose.

---

## 🧩 Overview

This project lets you review GitHub repositories using a **locally hosted LLM** (via Ollama), analyze the code for:

* 🔐 Security issues
* ⚙️ Performance inefficiencies
* 🧩 Infrastructure suitability (CPU, memory, ECS configurations)

All results are **stored in PostgreSQL** for audit and review — **no cloud AI services required.**

---

## 🧰 Tech Stack

| Component                  | Purpose                                        |
| -------------------------- | ---------------------------------------------- |
| 🐍 Python + Streamlit      | Interactive UI for code analysis               |
| 🧠 Ollama (phi3-mini)      | Local LLM for AI reasoning                     |
| 🐘 PostgreSQL              | Persistent data storage                        |
| 🐳 Docker + Docker Compose | One-command orchestration                      |
| ☁️ AWS EC2                 | Deployment environment (t3.medium recommended) |

---

## 🚀 Quick Start Guide

### 1️⃣ Clone the Project

```bash
git clone https://github.com/hanumathkrishna/devops-ai-reviewer
cd Devops-Ai-Reviewer
```

---

### 2️⃣ Launch the Stack

Run this one simple command to start everything:

```bash
docker compose up -d
```

This automatically launches:

* 🧠 **Ollama** → Local LLM model runtime
* 🐘 **PostgreSQL** → Database to store analysis reports
* 💻 **Streamlit App** → Frontend for UI interaction

---

### 3️⃣ Pull the Ollama Model (🔴 Required Once)

Before using the app, you must download the LLM model *inside the Ollama container*.

Run this command **once only**:

```bash
docker exec -it ollama ollama pull phi3:mini
```

✅ This will:

* Download the **phi3-mini** model
* Cache it in the Docker volume (`ollama_models`)
* Persist even after container restarts

⚠️ If you skip this step, Ollama will show an error:
`model "phi3:mini" not found`

---

### 4️⃣ Access the App

Open your browser and navigate to:

```
http://<EC2-Public-IP>:8501
```

or locally:

```
http://localhost:8501
```

You’ll see the Streamlit interface:

* Enter your **GitHub Personal Access Token**
* Select a **repository and branch**
* Input **service type, vCPU, and memory**
* Click **“Analyze Code”**

The AI will:

* Review code quality
* Detect performance/security issues
* Evaluate if infra specs are suitable (e.g., ECS/Fargate)
* Save results automatically in PostgreSQL 🎯

---

## ⚙️ EC2 Deployment Notes

You can deploy this on an **AWS Ubuntu EC2 t3.medium** instance easily.

### Steps:

1. Launch EC2 (Ubuntu 22.04 LTS, 2 vCPU, 4GB RAM)
2. Open these **ports** in Security Group:

| Port    | Service    | Description                    |
| ------- | ---------- | ------------------------------ |
| `8501`  | Streamlit  | Web UI access                  |
| `11434` | Ollama     | Local LLM endpoint             |
| `5432`  | PostgreSQL | (Optional) for DB access/debug |
| `22`    | SSH        | EC2 management                 |

3. Install Docker and Compose once:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
```

4. Logout & re-login, then follow the **Quick Start steps** above.

---

## 🧠 How It Works

1. **User Login:** Authenticate to GitHub using a personal access token.
2. **Code Fetching:** App fetches code recursively from selected repo and branch.
3. **Infra Input:** You provide infra specs (like ECS vCPU, memory).
4. **AI Review:** Ollama LLM analyzes the source for:

   * Security flaws
   * Performance inefficiencies
   * Infrastructure fit
5. **Result Storage:** Review results are stored in PostgreSQL with repo name, timestamp, and config.

---

## 🐘 PostgreSQL Details

* **DB Name:** `aidevops`
* **User:** `aiuser`
* **Password:** `aisecret`

### Persistent Storage

Postgres data is stored in the Docker volume `pgdata`.

Even if you restart EC2:

```bash
docker compose down
docker compose up -d
```

Your database and models remain intact ✅

---

### View Data Inside Postgres

To manually inspect stored results:

```bash
docker exec -it postgres psql -U aiuser -d aidevops
select * from reviews;
```

---

## 🧩 Docker Compose Summary

```yaml
services:
  ollama:   # AI model runtime
  postgres: # Database
  app:      # Streamlit UI
volumes:
  ollama_models:
  pgdata:
```

To stop:

```bash
docker compose down
```

To stop & delete all data (DB + model cache):

```bash
docker compose down -v
```

---

## 🧠 Changing Models

You can upgrade to a stronger model anytime:

```bash
docker exec -it ollama ollama pull llama3.1
```

Then modify in `app.py`:

```python
MODEL_NAME = "llama3.1"
```

---

## 🧾 Example Workflow

1. 🧑‍💻 Enter GitHub token
2. 📦 Select repository
3. ⚙️ Define infrastructure specs
4. 🤖 Click “Analyze Code”
5. 🧾 View AI insights directly in the Streamlit UI
6. 💾 Results automatically stored in PostgreSQL

---

## 🧱 System Requirements

| Resource      | Recommended                     |
| ------------- | ------------------------------- |
| Instance Type | t3.medium or higher             |
| RAM           | ≥ 4 GB                          |
| Disk          | ≥ 10 GB                         |
| OS            | Ubuntu 20.04+                   |
| Ollama Model  | phi3:mini                       |
| Python        | 3.11 (handled inside container) |

---

## 🧹 Cleanup Commands

To stop the containers:

```bash
docker compose down
```

To remove everything including model and DB data:

```bash
docker compose down -v
```

To view running containers:

```bash
docker ps
```

---
