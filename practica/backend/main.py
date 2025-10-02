import os
import datetime
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import List
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#MongoDB Colection
mongo_uri = os.getenv("MONGO_URI", "mongodb://admin_user:web3@mongo:27017/")
mongo_client = MongoClient(mongo_uri)
database = mongo_client.practica1
collection_historial = database.historial


# Modelo de entrada para suma
class Operacion(BaseModel):
    numeros: List[float] = Field(..., min_items=2)

@app.post("/calculadora/sum")
def sumar(op: Operacion):
    """
    Suma de una lista de números enviada en el body (JSON).
    Ejemplo: { "numeros": [5, 10, 15] }
    """
    result = sum(op.numeros)

    document = {
        "numeros": op.numeros,
        "resultado": result,
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }

    collection_historial.insert_one(document)

    return {"numeros": op.numeros, "resultado": result}

@app.get("/calculadora/sum")
def sumar_query(a: float = Query(...), b: float = Query(...)):
    """
    Suma de dos números enviados como parámetros en query (?a=...&b=...).
    """
    result = a + b

    document = {
        "a": a,
        "b": b,
        "resultado": result,
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }

    collection_historial.insert_one(document)

    return {"a": a, "b": b, "resultado": result}

@app.get("/calculadora/historial")
def obtener_historial():
    try:
        operaciones = collection_historial.find({})
        historial = []
        for operacion in operaciones:
            if "a" in operacion and "b" in operacion:
                numeros = [operacion.get("a"), operacion.get("b")]
            elif "numeros" in operacion:
                numeros = operacion.get("numeros", [])
            else:
                numeros = []
            historial.append({
                "numeros": numeros,
                "resultado": operacion.get("resultado"),
                "date": operacion.get("date").isoformat() if isinstance(operacion.get("date"), datetime.datetime) else str(operacion.get("date"))
            })
        return {"historial": historial}
    except Exception as e:
        print("Error en historial:", e)
        return {"error": str(e)}