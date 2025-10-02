import os
import datetime
from fastapi import FastAPI
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#MongoDB Colection
mongo_uri = os.getenv("MONGO_URI", "mongodb://admin_user:web3@mongo:27017/")
mongo_client = MongoClient(mongo_uri)
database = mongo_client.practica1
collection_historial = database.historial

@app.get("/calculadora/sum")
def sumar(a: float, b: float):
    """
    Suma de dos números que viene como parámetros e query (?a=...&b=...)
    Ejemplo: /calculadora/sum?a=5&b=10
    """

    result = a + b

    document = {
        "resultado": result,
        "a": a,
        "b": b,
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }

    collection_historial.insert_one(document)

    return {"a": a, "b": b, "resultado": result}

@app.get("/calculadora/historial")
def obtener_historial():
    operaciones = collection_historial.find({})
    historial = []
    for operacion in operaciones:
        historial.append({
            "a": operacion["a"],
            "b": operacion["b"],
            "resultado": operacion["resultado"],
            "date": operacion.get("date").isoformat() if isinstance(operacion.get("date"), datetime.datetime) else str(operacion.get("date"))
        })
    return {"historial": historial}