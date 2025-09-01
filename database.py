import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno (Render también las maneja automáticamente)
load_dotenv()

# URL de la base de datos desde Render
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ No se encontró la variable DATABASE_URL. Verifica en Render Config Vars.")

# Render entrega la URL con "postgres://", pero SQLAlchemy requiere "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# SessionLocal → se usará en las rutas para obtener la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


# ==========================
# 📌 Dependencia para FastAPI
# ==========================
def get_db():
    """
    Genera una sesión de BD para inyectar en los endpoints de FastAPI.
    Se asegura de cerrarla después de usarla.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
