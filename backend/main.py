import uuid # Para generar IDs únicos
from typing import List # Para listas en type hints
from fastapi import FastAPI, HTTPException, status # Importamos status para códigos HTTP
from pydantic import BaseModel, EmailStr # BaseModel para crear modelos, EmailStr para validar emails

# --- Modelos de Datos (Pydantic) ---

# Modelo para los datos que esperamos recibir al crear un proyecto
class ProjectCreate(BaseModel):
    name: str
    owner: str
    location: str
    sector: str
    email: EmailStr # Valida automáticamente que sea un formato de email válido

# Modelo para los datos que devolveremos al mostrar un proyecto (incluye ID)
class ProjectDisplay(BaseModel):
    id: uuid.UUID
    name: str
    owner: str
    location: str
    sector: str
    email: EmailStr

# --- "Base de datos" Temporal (en memoria) ---
# Una lista simple para guardar los proyectos mientras probamos.
# ¡Esto se perderá cada vez que reinicies el servidor! Lo reemplazaremos después.
projects_db: List[ProjectDisplay] = []

# --- Aplicación FastAPI ---

app = FastAPI(
    title="API Plataforma Contenidos IA",
    version="0.1.0",
    description="API para gestionar la generación de contenidos web con IA."
    )

# --- Endpoints ---

@app.get("/")
async def read_root():
    """
    Endpoint raíz que devuelve un saludo.
    """
    return {"message": "API de la Plataforma de Contenidos funcionando!"}

@app.post("/projects/", response_model=ProjectDisplay, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate):
    """
    Crea un nuevo proyecto y lo guarda en nuestra 'base de datos' temporal.
    """
    # Genera un ID único para el proyecto
    project_id = uuid.uuid4()

    # Crea el objeto del proyecto como lo vamos a guardar/mostrar (con ID)
    new_project = ProjectDisplay(
        id=project_id,
        name=project_in.name,
        owner=project_in.owner,
        location=project_in.location,
        sector=project_in.sector,
        email=project_in.email
    )

    # Añade el nuevo proyecto a nuestra lista temporal
    projects_db.append(new_project)

    # Devuelve el proyecto recién creado
    return new_project

@app.get("/projects/", response_model=List[ProjectDisplay])
async def list_projects():
    """
    Devuelve una lista de todos los proyectos en nuestra 'base de datos' temporal.
    """
    return projects_db

# (Aquí añadiremos más endpoints después: get por ID, update, delete, etc.)