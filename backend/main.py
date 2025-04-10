from fastapi import FastAPI

# Crear una instancia de la aplicación FastAPI
app = FastAPI(title="API Plataforma Contenidos IA", version="0.1.0")

# Definir un endpoint básico en la raíz ("/")
@app.get("/")
async def read_root():
    """
    Endpoint raíz que devuelve un saludo.
    """
    return {"message": "Hola! Bienvenido a la API de la Plataforma de Contenidos."}

# (Aquí añadiremos más endpoints y lógica después)