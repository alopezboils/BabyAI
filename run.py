#!/usr/bin/env python3
"""
babyAI Launcher
Arranca el backend FastAPI y sirve el frontend estático.
Uso: python run.py
"""
import subprocess
import sys
import os
import webbrowser
import threading
import time

BASE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(BASE, "backend", "server.py")
FRONTEND = os.path.join(BASE, "frontend")

def check_deps():
    deps = ["fastapi", "uvicorn", "chromadb", "ollama", "sentence_transformers"]
    missing = []
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    if missing:
        print(f"Instalando dependencias: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

def start_backend():
    os.chdir(os.path.join(BASE, "backend"))
    subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "server:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

def start_frontend():
    os.chdir(FRONTEND)
    subprocess.Popen([
        sys.executable, "-m", "http.server", "3000",
        "--bind", "0.0.0.0"
    ])

def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:3000")

if __name__ == "__main__":
    print("🚀 Arrancando babyAI...")
    check_deps()
    start_backend()
    start_frontend()
    threading.Thread(target=open_browser, daemon=True).start()
    print("✅ babyAI corriendo en http://localhost:3000")
    print("   Backend API en http://localhost:8000")
    print("   Pulsa Ctrl+C para parar")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nbabyAI apagado. ¡Hasta pronto!")
