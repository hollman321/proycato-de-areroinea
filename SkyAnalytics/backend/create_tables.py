import os
from sqlalchemy import create_engine
from models import Base

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://admin:secretpassword@localhost:5432/skyanalytics')

# Crear el engine
engine = create_engine(DATABASE_URL)

# Crear todas las tablas definidas en los modelos
Base.metadata.create_all(engine)

print("Tablas creadas exitosamente en la base de datos.")