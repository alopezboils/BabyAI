# BabyAI
# 🤖 babyAI

> Tu mascota robot inteligente

![GitHub release](https://img.shields.io/github/v/release/TU_USUARIO/babyAI?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow?style=flat-square)

babyAI es una mascota virtual tipo Pou pero con IA real. Aprende de cada conversación, recuerda lo que le dices y mejora con el tiempo gracias a memoria vectorial (ChromaDB) y un LLM local (Ollama).

---

## ⬇️ Descarga

Ve a la sección [**Releases**](../../releases/latest) y descarga el archivo para tu sistema:

| Sistema | Archivo |
|---------|---------|
| Windows | `babyAI-Windows.zip` |
| macOS   | `babyAI-macOS.zip`   |
| Linux   | `babyAI-Linux.zip`   |

---

## 🚀 Instalación en PC

### 1. Instala Ollama (solo la primera vez)

Descarga desde [ollama.ai](https://ollama.ai) e instálalo. Luego abre una terminal y ejecuta:

```bash
ollama pull phi3:mini
```

### 2. Ejecuta babyAI

1. Descomprime el `.zip` descargado donde quieras
2. Entra en la carpeta `babyAI`
3. Ejecuta `babyAI.exe` (Windows) o `babyAI` (Mac/Linux)
4. Se abre automáticamente el navegador en **http://localhost:3000**

> La primera vez tarda un poco en arrancar porque carga el modelo de embeddings.

---

## 📱 Instalar en el móvil (sin cables, sin tienda de apps)

babyAI funciona como una **PWA** (Progressive Web App): se instala directamente desde el navegador del móvil y queda en la pantalla de inicio como una app nativa.

**Requisito**: el móvil y el PC deben estar en la **misma red WiFi**.

### Paso 1 — Encuentra la IP de tu PC

**Windows:**
```
Abre cmd → escribe: ipconfig
Busca "Dirección IPv4", algo como 192.168.1.XX
```

**Mac/Linux:**
```bash
ifconfig | grep "inet "
```

### Paso 2 — Abre babyAI en el móvil

En el navegador del móvil escribe:
```
http://192.168.1.XX:3000
```
(sustituye `192.168.1.XX` por la IP de tu PC)

### Paso 3 — Instala en la pantalla de inicio

**Android (Chrome):**
> Menú (tres puntos) → "Añadir a pantalla de inicio" → "Instalar"

**iPhone / iPad (Safari):**
> Botón compartir (cuadrado con flecha) → "Añadir a pantalla de inicio"

¡Listo! babyAI aparece en tu pantalla de inicio como cualquier otra app 🎉

---

## 🎮 Cómo usar babyAI

| Acción | Qué hace |
|--------|----------|
| **Tocar la mascota** | babyAI reacciona y sus ojos brillan |
| **🍬 Alimentar** | Sube la energía |
| **🎮 Jugar** | Sube la felicidad |
| **🧠 Entrenar** | Sube la inteligencia y XP |
| **💾 Memoria** | Muestra estadísticas y historial |
| **Chat** | Habla con la IA, que aprende y recuerda |
| **Feedback 👍/👎** | Enseña a babyAI qué respuestas son buenas |

Las estadísticas (felicidad, energía) bajan con el tiempo — ¡cuida a tu babyAI!

---

## 🏗️ Estructura del proyecto

```
babyAI-app/
├── .github/
│   └── workflows/
│       └── release.yml     ← Build automático en GitHub Actions
├── backend/
│   └── server.py           ← API FastAPI (lógica IA, memoria vectorial)
├── frontend/
│   ├── index.html          ← App PWA completa (mascota Wall-E + chat)
│   ├── manifest.json       ← Config instalación PWA
│   └── sw.js               ← Service Worker (offline)
├── launcher.py             ← Punto de entrada del ejecutable
├── babyAI.spec             ← Config PyInstaller
├── run.py                  ← Arranque manual (desarrollo)
├── babyAI.bat              ← Acceso directo Windows
└── babyAI.sh               ← Acceso directo Mac/Linux
```

---

## 🔧 Desarrollo / Contribuir

```bash
git clone https://github.com/TU_USUARIO/babyAI
cd babyAI

pip install fastapi uvicorn chromadb sentence-transformers ollama pydantic

python run.py
# Abre http://localhost:3000
```

### Crear una nueva release

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions compila automáticamente los ejecutables para Windows, macOS y Linux y los adjunta a la release.

---

## 📦 Tecnologías

- **Frontend**: HTML/CSS/JS puro · PWA · Service Worker
- **Backend**: FastAPI · Python 3.11
- **IA**: Ollama (phi3:mini) · ChromaDB · sentence-transformers
- **Build**: PyInstaller · GitHub Actions

---

## ⚠️ Notas

- La memoria de babyAI se guarda en la carpeta `memoria_ia/` junto al ejecutable. No la borres o perderá sus recuerdos.
- Ollama debe estar corriendo en segundo plano para que el chat funcione.
- En Mac puede que el sistema pida permiso para abrir una app de desarrollador desconocido: Sistema → Seguridad → "Abrir de todas formas".
