import os
import datetime
from fastapi import FastAPI, Query, HTTPException
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

# Helper para normalizar datetime a ISO-8601 con 'Z'
def _to_iso_z(dt):
    if isinstance(dt, datetime.datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        else:
            dt = dt.astimezone(datetime.timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")
    return str(dt)


# Modelo de entrada para suma
class Operacion(BaseModel):
    cantidad: int
    numeros: List[float]

@app.post("/calculadora/sum")
def sumar(op: Operacion):
    """
    Suma de una lista de números enviada en el body (JSON).
    El usuario debe indicar la cantidad de números y proporcionar exactamente esa cantidad en la lista.
    Ejemplo: { "cantidad": 3, "numeros": [5, 10, 15] }
    """
    if len(op.numeros) != op.cantidad:
        raise HTTPException(status_code=400, detail="La cantidad de números no coincide con la longitud de la lista 'numeros'.")
    if len(op.numeros) < 2:
        raise HTTPException(status_code=400, detail="Se requieren al menos 2 operandos")
    if any(num < 0 for num in op.numeros):
        raise HTTPException(status_code=400, detail="No se permiten números negativos en la lista 'numeros'.")
    
    result = sum(op.numeros)

    document = {
        "numeros": op.numeros,
        "resultado": result,
        "operacion": "suma",
        "date": datetime.datetime.now(datetime.timezone.utc),
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
        "operacion": "suma",
        "date": datetime.datetime.now(datetime.timezone.utc),
    }

    collection_historial.insert_one(document)

    return {"a": a, "b": b, "resultado": result}

@app.post("/calculadora/resta")
def restar(op: Operacion):
    """
    Resta secuencial de una lista de números enviada en el body (JSON).
    El usuario debe indicar la cantidad de números y proporcionar exactamente esa cantidad en la lista.
    Ejemplo: { "cantidad": 3, "numeros": [20, 5, 3] } => 20 - 5 - 3 = 12
    """
    if len(op.numeros) != op.cantidad:
        raise HTTPException(status_code=400, detail="La cantidad de números no coincide con la longitud de la lista 'numeros'.")
    if len(op.numeros) < 2:
        raise HTTPException(status_code=400, detail="Se requieren al menos 2 operandos")
    if any(num < 0 for num in op.numeros):
        raise HTTPException(status_code=400, detail="No se permiten números negativos en la lista 'numeros'.")
    
    result = op.numeros[0]
    for num in op.numeros[1:]:
        result -= num

    document = {
        "numeros": op.numeros,
        "resultado": result,
        "operacion": "resta",
        "date": datetime.datetime.now(datetime.timezone.utc),
    }

    collection_historial.insert_one(document)

    return {"numeros": op.numeros, "resultado": result}

@app.post("/calculadora/multiplicacion")
def multiplicar(op: Operacion):
    """
    Multiplicación de una lista de números enviada en el body (JSON).
    El usuario debe indicar la cantidad de números y proporcionar exactamente esa cantidad en la lista.
    Ejemplo: { "cantidad": 3, "numeros": [2, 3, 4] } => 2 * 3 * 4 = 24
    """
    if len(op.numeros) != op.cantidad:
        raise HTTPException(status_code=400, detail="La cantidad de números no coincide con la longitud de la lista 'numeros'.")
    if len(op.numeros) < 2:
        raise HTTPException(status_code=400, detail="Se requieren al menos 2 operandos")
    if any(num < 0 for num in op.numeros):
        raise HTTPException(status_code=400, detail="No se permiten números negativos en la lista 'numeros'.")
    
    result = 1
    for num in op.numeros:
        result *= num

    document = {
        "numeros": op.numeros,
        "resultado": result,
        "operacion": "multiplicacion",
        "date": datetime.datetime.now(datetime.timezone.utc),
    }

    collection_historial.insert_one(document)

    return {"numeros": op.numeros, "resultado": result}

@app.post("/calculadora/division")
def dividir(op: Operacion):
    """
    División secuencial de una lista de números enviada en el body (JSON).
    El usuario debe indicar la cantidad de números y proporcionar exactamente esa cantidad en la lista.
    Se lanza un HTTPException si algún divisor es cero.
    Ejemplo: { "cantidad": 3, "numeros": [20, 2, 2] } => 20 / 2 / 2 = 5
    """
    if len(op.numeros) != op.cantidad:
        raise HTTPException(status_code=400, detail="La cantidad de números no coincide con la longitud de la lista 'numeros'.")
    if len(op.numeros) < 2:
        raise HTTPException(status_code=400, detail="Se requieren al menos 2 operandos")
    if any(num < 0 for num in op.numeros):
        raise HTTPException(status_code=400, detail="No se permiten números negativos en la lista 'numeros'.")
    
    result = op.numeros[0]
    for num in op.numeros[1:]:
        if num == 0:
            raise HTTPException(status_code=400, detail="División por cero no permitida.")
        result /= num

    document = {
        "numeros": op.numeros,
        "resultado": result,
        "operacion": "division",
        "date": datetime.datetime.now(datetime.timezone.utc),
    }

    collection_historial.insert_one(document)

    return {"numeros": op.numeros, "resultado": result}

@app.get("/calculadora/historial")
def obtener_historial(
    operacion: str = Query(None, description="Tipo de operación: suma, resta, multiplicacion, division"),
    fecha: str = Query(None, description="Fecha exacta en formato YYYY-MM-DD"),
    fecha_inicio: str = Query(None, description="Fecha inicio en formato YYYY-MM-DD"),
    fecha_fin: str = Query(None, description="Fecha fin en formato YYYY-MM-DD"),
    orden_fecha: str = Query(None, description="asc o desc para ordenar por fecha"),
    orden_resultado: str = Query(None, description="asc o desc para ordenar por resultado"),
):
    try:
        filtro = {}
        # Filtro por tipo de operación
        if operacion:
            if operacion == "suma":
                filtro["$or"] = [{"operacion": "suma"}, {"operacion": {"$exists": False}}]
            else:
                filtro["operacion"] = operacion

        # Filtro por fechas
        date_filter = {}
        if fecha:
            try:
                dt = datetime.datetime.strptime(fecha, "%Y-%m-%d")
                dt_start = datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0)
                dt_end = datetime.datetime(dt.year, dt.month, dt.day, 23, 59, 59, 999999)
                date_filter["$gte"] = dt_start
                date_filter["$lte"] = dt_end
            except Exception as e:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido (YYYY-MM-DD)")
        else:
            if fecha_inicio:
                try:
                    dt_start = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
                    dt_start = datetime.datetime(dt_start.year, dt_start.month, dt_start.day, 0, 0, 0)
                    date_filter["$gte"] = dt_start
                except Exception as e:
                    raise HTTPException(status_code=400, detail="Formato de fecha_inicio inválido (YYYY-MM-DD)")
            if fecha_fin:
                try:
                    dt_end = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d")
                    dt_end = datetime.datetime(dt_end.year, dt_end.month, dt_end.day, 23, 59, 59, 999999)
                    date_filter["$lte"] = dt_end
                except Exception as e:
                    raise HTTPException(status_code=400, detail="Formato de fecha_fin inválido (YYYY-MM-DD)")
        if date_filter:
            filtro["date"] = date_filter

        # Ordenamiento
        sort_fields = []
        if orden_fecha:
            if orden_fecha.lower() == "asc":
                sort_fields.append(("date", 1))
            elif orden_fecha.lower() == "desc":
                sort_fields.append(("date", -1))
        if orden_resultado:
            if orden_resultado.lower() == "asc":
                sort_fields.append(("resultado", 1))
            elif orden_resultado.lower() == "desc":
                sort_fields.append(("resultado", -1))

        # Consulta a MongoDB
        if sort_fields:
            operaciones = collection_historial.find(filtro).sort(sort_fields)
        else:
            # Orden por fecha descendente por defecto
            operaciones = collection_historial.find(filtro).sort("date", -1)

        historial = []
        for operacion_doc in operaciones:
            if "a" in operacion_doc and "b" in operacion_doc:
                numeros = [operacion_doc.get("a"), operacion_doc.get("b")]
            elif "numeros" in operacion_doc:
                numeros = operacion_doc.get("numeros", [])
            else:
                numeros = []
            historial.append({
                "numeros": numeros,
                "resultado": operacion_doc.get("resultado"),
                "operacion": operacion_doc.get("operacion", "suma"),
                "date": _to_iso_z(operacion_doc.get("date"))
            })
        return {"historial": historial}
    except Exception as e:
        print("Error en historial:", e)
        return {"error": str(e)}