"""
babyAI - Servidor FastAPI
Expone la lógica del babyAI original como API REST.
Requiere: pip install fastapi uvicorn chromadb ollama sentence-transformers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import ollama
import json
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer

# ── Configuración ──────────────────────────────────────────
CARPETA = "memoria_ia"
ARCHIVO_EPISODICO = os.path.join(CARPETA, "episodico.json")
ARCHIVO_STATS = os.path.join(CARPETA, "stats.json")
MODELO_LLM = "phi3:mini"
MODELO_EMBEDDING = "all-MiniLM-L6-v2"
RECUERDOS_A_USAR = 4

# ── Inicialización ─────────────────────────────────────────
os.makedirs(CARPETA, exist_ok=True)

cliente_chroma = chromadb.PersistentClient(path=os.path.join(CARPETA, "chroma_db"))
coleccion = cliente_chroma.get_or_create_collection("recuerdos")
embedder = SentenceTransformer(MODELO_EMBEDDING)

app = FastAPI(title="babyAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Modelos Pydantic ───────────────────────────────────────
class MensajeRequest(BaseModel):
    pregunta: str
    historial: list = []

class FeedbackRequest(BaseModel):
    pregunta: str
    respuesta: str
    tipo: str          # "positivo", "negativo", "neutro"
    comentario: str = ""

class StatsUpdate(BaseModel):
    felicidad: int
    energia: int
    inteligencia: int

# ── Helpers ────────────────────────────────────────────────
def cargar_episodico():
    if os.path.exists(ARCHIVO_EPISODICO):
        with open(ARCHIVO_EPISODICO, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_episodico(episodios):
    with open(ARCHIVO_EPISODICO, "w", encoding="utf-8") as f:
        json.dump(episodios, f, ensure_ascii=False, indent=2)

def cargar_stats():
    defaults = {"felicidad": 70, "energia": 60, "inteligencia": 50, "nivel": 1, "xp": 0}
    if os.path.exists(ARCHIVO_STATS):
        with open(ARCHIVO_STATS, "r", encoding="utf-8") as f:
            return {**defaults, **json.load(f)}
    return defaults

def guardar_stats(stats):
    with open(ARCHIVO_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def guardar_recuerdo(texto, metadatos):
    vector = embedder.encode(texto).tolist()
    id_unico = f"recuerdo_{datetime.now().timestamp()}"
    coleccion.add(ids=[id_unico], embeddings=[vector], documents=[texto], metadatas=[metadatos])

def buscar_recuerdos_relevantes(consulta, n=RECUERDOS_A_USAR):
    if coleccion.count() == 0:
        return []
    vector = embedder.encode(consulta).tolist()
    resultados = coleccion.query(
        query_embeddings=[vector],
        n_results=min(n, coleccion.count())
    )
    return resultados["documents"][0] if resultados["documents"] else []

def autoevaluar(pregunta, respuesta):
    prompt_eval = f"""Evalúa esta respuesta del 1 al 10 y en UNA frase corta di qué mejorarías.
Pregunta: {pregunta}
Respuesta: {respuesta}
Responde SOLO en este formato JSON: {{"puntuacion": 8, "mejora": "ser más concreto"}}"""
    try:
        resultado = ollama.chat(model=MODELO_LLM, messages=[{"role": "user", "content": prompt_eval}])
        texto = resultado["message"]["content"].strip()
        inicio = texto.find("{")
        fin = texto.rfind("}") + 1
        if inicio >= 0 and fin > inicio:
            return json.loads(texto[inicio:fin])
    except:
        pass
    return {"puntuacion": 7, "mejora": "ninguna identificada"}

# ── Endpoints ──────────────────────────────────────────────
@app.get("/estado")
def get_estado():
    """Devuelve stats del babyAI y recuento de memoria."""
    stats = cargar_stats()
    episodios = cargar_episodico()
    return {
        "stats": stats,
        "recuerdos_totales": coleccion.count(),
        "sesiones": len(episodios),
        "ultimas_interacciones": episodios[-5:] if episodios else [],
    }

@app.post("/chat")
def chat(req: MensajeRequest):
    """Procesa una pregunta y devuelve la respuesta del LLM con contexto de memoria."""
    recuerdos = buscar_recuerdos_relevantes(req.pregunta)
    contexto_memoria = ""
    if recuerdos:
        contexto_memoria = "\n\nRecuerdos de conversaciones anteriores:\n" + "".join(f"- {r}\n" for r in recuerdos)

    sistema = (
        "Eres babyAI, una mascota virtual inteligente y cariñosa. "
        "Aprendes y mejoras con cada conversación. "
        "Usa los recuerdos anteriores para personalizar tus respuestas. "
        "Si un recuerdo indica un error, no lo repitas. "
        "Responde siempre de forma cálida, breve y clara." + contexto_memoria
    )

    historial = [{"role": m["role"], "content": m["content"]} for m in req.historial]
    historial.append({"role": "user", "content": req.pregunta})

    resultado = ollama.chat(
        model=MODELO_LLM,
        messages=[{"role": "system", "content": sistema}] + historial
    )
    respuesta = resultado["message"]["content"]

    autoeval = autoevaluar(req.pregunta, respuesta)

    # Subir inteligencia y XP por cada conversación
    stats = cargar_stats()
    stats["inteligencia"] = min(100, stats["inteligencia"] + 2)
    stats["xp"] = stats.get("xp", 0) + 10
    if stats["xp"] >= stats["nivel"] * 100:
        stats["nivel"] += 1
    guardar_stats(stats)

    return {
        "respuesta": respuesta,
        "autoeval": autoeval,
        "stats": stats,
        "recuerdos_usados": len(recuerdos),
    }

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    """Guarda el feedback del usuario en memoria vectorial y episódica."""
    sesion_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    if req.tipo == "negativo" and req.comentario:
        aprendizaje = f"ERROR A EVITAR — {req.comentario}"
        nota = 3
    elif req.tipo == "positivo":
        aprendizaje = "RESPUESTA BUENA — usar este enfoque"
        nota = 9
    else:
        aprendizaje = "Interacción neutra"
        nota = 6

    texto_recuerdo = (
        f"Pregunta: {req.pregunta} | "
        f"Respuesta: {req.respuesta[:200]} | "
        f"{aprendizaje}"
    )
    guardar_recuerdo(texto_recuerdo, {
        "fecha": datetime.now().isoformat(),
        "nota": str(nota),
        "feedback_tipo": req.tipo,
        "sesion": sesion_id,
    })

    episodios = cargar_episodico()
    episodios.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tema": req.pregunta[:60],
        "nota_final": nota,
        "feedback_tipo": req.tipo,
        "comentario_feedback": req.comentario,
        "sesion": sesion_id,
    })
    guardar_episodico(episodios)

    # Actualizar felicidad según feedback
    stats = cargar_stats()
    if req.tipo == "positivo":
        stats["felicidad"] = min(100, stats["felicidad"] + 8)
    elif req.tipo == "negativo":
        stats["felicidad"] = max(0, stats["felicidad"] - 5)
    guardar_stats(stats)

    return {"ok": True, "recuerdos_totales": coleccion.count()}

@app.post("/accion/{accion}")
def accion(accion: str):
    """Procesa acciones de la mascota: feed, play, train."""
    stats = cargar_stats()
    mensaje = ""
    if accion == "feed":
        stats["energia"] = min(100, stats["energia"] + 15)
        stats["felicidad"] = min(100, stats["felicidad"] + 5)
        mensaje = "¡Mmm, datos deliciosos! Me siento con más energía."
    elif accion == "play":
        stats["felicidad"] = min(100, stats["felicidad"] + 18)
        stats["energia"] = max(0, stats["energia"] - 10)
        mensaje = "¡Me encanta jugar contigo! Cada vez aprendo más."
    elif accion == "train":
        stats["inteligencia"] = min(100, stats["inteligencia"] + 10)
        stats["energia"] = max(0, stats["energia"] - 12)
        stats["xp"] = stats.get("xp", 0) + 20
        if stats["xp"] >= stats["nivel"] * 100:
            stats["nivel"] += 1
        mensaje = "¡Procesando nuevos patrones! Mi mente crece."
    else:
        return {"error": "Acción desconocida"}

    guardar_stats(stats)
    return {"mensaje": mensaje, "stats": stats}

@app.get("/memoria")
def get_memoria():
    """Devuelve estadísticas de memoria y últimas interacciones."""
    episodios = cargar_episodico()
    positivos = sum(1 for e in episodios if e.get("feedback_tipo") == "positivo")
    negativos = sum(1 for e in episodios if e.get("feedback_tipo") == "negativo")
    return {
        "recuerdos_vectoriales": coleccion.count(),
        "sesiones": len(episodios),
        "feedbacks_positivos": positivos,
        "feedbacks_negativos": negativos,
        "historial": episodios[-20:],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
