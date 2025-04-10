from contextlib import asynccontextmanager # Para lifespan events
from typing import List, Optional # Optional es necesario para el ID de la tabla
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import EmailStr # Mantenemos EmailStr para validación de entrada
from sqlmodel import Field, Session, SQLModel, create_engine, select # Nuevos imports de SQLModel

# --- Modelo de Datos de Entrada (Pydantic puro, sin cambios) ---
# Se usa para validar los datos que LLEGAN a la API al crear
class ProjectCreate(SQLModel): # Cambiado a SQLModel para posible reutilización, pero sin table=True
    name: str
    owner: str
    location: str
    sector: str
    email: EmailStr

# --- Modelo de Tabla de Base de Datos (SQLModel) ---
# Hereda de SQLModel, representa la tabla en la BD
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # ID entero autoincremental
    name: str = Field(index=True) # Indexamos el nombre para búsquedas rápidas (ej. futuro)
    owner: str
    location: str
    sector: str
    email: EmailStr # Se guarda como string pero validado al entrar

# --- Modelo de Datos de Salida (SQLModel) ---
# Lo que la API devolverá. Incluye el ID. Hereda del modelo de tabla.
class ProjectRead(Project):
    pass # Por ahora es igual que el modelo de tabla, pero podría diferir

# --- Configuración de la Base de Datos ---

DATABASE_FILE = "database.db" # Nombre del archivo SQLite
DATABASE_URL = f"sqlite:///./{DATABASE_FILE}" # URL de conexión

# Creamos el "motor" de la base de datos. check_same_thread es necesario para SQLite.
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

# Función para crear las tablas en la BD si no existen
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- Context Manager para Lifespan Events (FastAPI) ---
# Código que se ejecuta al iniciar y al detener la aplicación

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código al inicio: Crear la base de datos y tablas
    print("INFO:     Creando base de datos y tablas si no existen...")
    create_db_and_tables()
    print("INFO:     Base de datos y tablas listas.")
    yield
    # Código al final (si fuera necesario)
    print("INFO:     La aplicación se está cerrando.")


# --- Aplicación FastAPI ---
# Incluimos el lifespan manager
app = FastAPI(
    title="API Plataforma Contenidos IA",
    version="0.1.0",
    description="API para gestionar la generación de contenidos web con IA.",
    lifespan=lifespan
    )

# --- Dependencia para obtener la Sesión de BD ---
# Crea una sesión por cada petición a la API y la cierra al terminar

def get_session():
    with Session(engine) as session:
        yield session

# --- Endpoints Modificados ---

@app.get("/")
async def read_root():
    """
    Endpoint raíz que devuelve un saludo.
    """
    return {"message": "API de la Plataforma de Contenidos funcionando con SQLite!"}

@app.post("/projects/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(*, session: Session = Depends(get_session), project_in: ProjectCreate):
    """
    Crea un nuevo proyecto y lo guarda en la base de datos SQLite.
    """
    # Crea una instancia del modelo de tabla a partir del modelo de entrada
    # Pydantic/SQLModel se encarga de la conversión si los nombres de campo coinciden
    db_project = Project.model_validate(project_in)

    # Añade el nuevo objeto a la sesión de BD
    session.add(db_project)
    # Guarda los cambios en la BD
    session.commit()
    # Refresca el objeto para obtener el ID asignado por la BD
    session.refresh(db_project)

    # Devuelve el objeto recién creado (incluyendo el ID de la BD)
    return db_project

@app.get("/projects/", response_model=List[ProjectRead])
async def list_projects(*, session: Session = Depends(get_session)):
    """
    Devuelve una lista de todos los proyectos desde la base de datos SQLite.
    """
    # Ejecuta una consulta para seleccionar todos los proyectos
    statement = select(Project)
    projects = session.exec(statement).all()
    # Devuelve la lista de proyectos
    return projects

# (Endpoints para get por ID, update, delete, etc. se añadirán después)