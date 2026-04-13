import streamlit as st
import requests, json, base64, psycopg2
from datetime import datetime
from github import Github, GithubException


st.set_page_config(page_title="🤖 DevOps AI Reviewer", page_icon="⚙️", layout="wide")


OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL_NAME = "phi3:mini"
DB_CONFIG = {
    "host": "postgres",
    "database": "aidevops",
    "user": "aiuser",
    "password": "aisecret"
}


def save_to_db(repo, service, vcpu, memory, result):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews(
                id SERIAL PRIMARY KEY,
                repo TEXT, service TEXT, vcpu FLOAT, memory FLOAT,
                analysis TEXT, created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute(
            "INSERT INTO reviews(repo,service,vcpu,memory,analysis) VALUES(%s,%s,%s,%s,%s)",
            (repo, service, vcpu, memory, result)
        )
        conn.commit(); cur.close(); conn.close()
    except Exception as e:
        st.error(f"DB error: {e}")


def get_code(repo, path, branch):
    try:
        contents = repo.get_contents(path, ref=branch)
        code = ""
        for c in contents if isinstance(contents, list) else [contents]:
            if c.type == "dir": code += get_code(repo, c.path, branch)
            else:
                try:
                    
                    code += base64.b64decode(c.content).decode("utf-8")
                except Exception: pass
        return code
    except Exception as e:
        st.error(f"GitHub error: {e}")
        return ""


st.sidebar.header("🔑 GitHub Connection")
token = st.sidebar.text_input("Personal Access Token", type="password")
repo = None

if token:
    try:
        gh = Github(token)
        user = gh.get_user()
        st.sidebar.success(f"✅ Logged in as {user.login}")
        repos = [r.full_name for r in user.get_repos()]
        rname = st.sidebar.selectbox("Select Repo", options=repos)
        if rname: repo = gh.get_repo(rname)
    except Exception as e:
        st.sidebar.error(f"Auth failed: {e}")


st.title("🤖 Local AI DevOps Reviewer")
if not repo:
    st.info("Connect GitHub in sidebar to continue.")
    st.stop()

st.success(f"Connected to {repo.full_name}")

col1, col2, col3 = st.columns(3)
with col1: service = st.text_input("Service (eg. AWS ECS Fargate)", "AWS ECS Fargate")
with col2: vcpu = st.number_input("vCPU", 0.25, 16.0, 2.0, 0.25)
with col3: memory = st.number_input("Memory (GB)", 0.5, 128.0, 4.0, 0.5)

branch = st.selectbox("Branch", [b.name for b in repo.get_branches()])
path = st.text_input("File/Folder Path", "/", "src/ or main.py")

if st.button("🔍 Analyze Code"):
    with st.spinner("Fetching code from GitHub..."):
        code = get_code(repo, path, branch)
    if not code: st.stop()

    prompt = f"""
    You are a DevSecOps expert.
    Evaluate this code for security, performance, and infra fit.
    Target: {service}, vCPU={vcpu}, Memory={memory}GB.
    ```
    {code}
    ```
    Return a structured analysis.
    """

    try:
        r = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt}, timeout=300)
        result = r.json().get("response", "No response.")
        
        st.write(result)
        save_to_db(repo.full_name, service, vcpu, memory, result)
        st.success("Saved to PostgreSQL ✅")
    except Exception as e:
        st.error(f"Ollama error: {e}")


