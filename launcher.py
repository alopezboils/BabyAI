"""
babyAI — launcher empaquetable con PyInstaller
Este archivo es el punto de entrada del ejecutable.
"""
import sys
import os
import threading
import time
import webbrowser
import subprocess

# Cuando está empaquetado, los recursos están en sys._MEIPASS
if getattr(sys, 'frozen', False):
    BASE = sys._MEIPASS
    WORK = os.path.dirname(sys.executable)
else:
    BASE = os.path.dirname(os.path.abspath(__file__))
    WORK = BASE

FRONTEND = os.path.join(BASE, "frontend")
BACKEND  = os.path.join(BASE, "backend")

sys.path.insert(0, BACKEND)

def start_frontend_server():
    import http.server
    import socketserver
    os.chdir(FRONTEND)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None  # silenciar logs
    with socketserver.TCPServer(("0.0.0.0", 3000), handler) as httpd:
        httpd.serve_forever()

def start_backend_server():
    os.chdir(WORK)
    # Crear carpeta de memoria en la misma carpeta que el ejecutable
    os.makedirs(os.path.join(WORK, "memoria_ia"), exist_ok=True)
    import uvicorn
    # Parchear la ruta de memoria para que sea relativa al ejecutable
    import server
    server.CARPETA = os.path.join(WORK, "memoria_ia")
    server.ARCHIVO_EPISODICO = os.path.join(server.CARPETA, "episodico.json")
    server.ARCHIVO_STATS     = os.path.join(server.CARPETA, "stats.json")
    uvicorn.run(server.app, host="127.0.0.1", port=8000, log_level="error")

def open_browser():
    time.sleep(2.5)
    webbrowser.open("http://localhost:3000")

if __name__ == "__main__":
    print("🤖 Arrancando babyAI...")

    t1 = threading.Thread(target=start_frontend_server, daemon=True)
    t2 = threading.Thread(target=start_backend_server,  daemon=True)
    t3 = threading.Thread(target=open_browser,          daemon=True)

    t1.start()
    t2.start()
    t3.start()

    print("✅ babyAI corriendo en http://localhost:3000")
    print("   Cierra esta ventana para apagar babyAI.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🤖 babyAI apagado. ¡Hasta pronto!")
