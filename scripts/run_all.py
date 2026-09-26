import subprocess
import sys
import time
import os
import signal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def main():
    print("=" * 70)
    print("🚀 Starting Customer Sentiment Analysis Dashboard (PRJ_382)")
    print("=" * 70)
    # --- Auto-setup for first-time users ---
    env_file = BASE_DIR / ".env"
    env_example = BASE_DIR / ".env.example"
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(str(env_example), str(env_file))
        print("[0/5] Created .env from .env.example (default config)")

    # Ensure saved_models directory exists
    (BASE_DIR / "backend" / "saved_models").mkdir(parents=True, exist_ok=True)

    # Step 1: Download spaCy model + train fallback + seed DB
    print("[1/5] Downloading spaCy language model (first run only)...")
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], cwd=str(BASE_DIR))

    print("[2/5] Training TF-IDF + Logistic Regression fallback model...")
    subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "train_fast_model.py")], cwd=str(BASE_DIR))

    print("[3/5] Seeding database with demo users and benchmark data...")
    subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "seed_data.py")], cwd=str(BASE_DIR))

    print("\n[4/5] Launching FastAPI Backend (:8000)...")
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
    ]
    backend_proc = subprocess.Popen(backend_cmd, cwd=str(BASE_DIR))

    # Give backend a moment to bind port
    time.sleep(2.5)

    print("\n[5/5] Launching Streamlit Interactive Dashboard (:8501)...")
    frontend_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(BASE_DIR / "frontend" / "app.py"),
        "--server.port",
        "8501",
        "--server.headless",
        "true",
    ]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=str(BASE_DIR))

    print("\n" + "=" * 70)
    print("✅ System Operational:")
    print("   👉 Streamlit Dashboard:  http://localhost:8501")
    print("   👉 FastAPI REST Docs:    http://localhost:8000/docs")
    print("   👉 Default Admin Login:  admin@sentiment.io / admin123")
    print("   👉 Default Analyst Login: analyst@sentiment.io / analyst123")
    print("   👉 Default Viewer Login:  viewer@sentiment.io / viewer123")
    print("=" * 70)
    print("Press Ctrl+C to terminate both servers.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("Done.")


if __name__ == "__main__":
    main()
