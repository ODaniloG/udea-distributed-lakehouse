import pandas as pd
import numpy as np
from faker import Faker
from pathlib import Path
import random

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

fake = Faker('es_CO')

np.random.seed(42)
random.seed(42)

# =========================================================
# CREAR CARPETA BRONZE
# =========================================================

BRONZE = Path("lakehouse/bronze")
BRONZE.mkdir(parents=True, exist_ok=True)

# =========================================================
# PARÁMETROS DEL SISTEMA
# =========================================================

NUM_ESTUDIANTES = 200000
NUM_CURSOS = 500
NUM_INSCRIPCIONES = 500000

# =========================================================
# SEDES
# =========================================================

sedes = [
    "Medellin",
    "Uraba",
    "Oriente",
    "Bajo Cauca"
]

# =========================================================
# FACULTADES
# =========================================================

facultades = [
    "Ingenieria",
    "Medicina",
    "Derecho",
    "Artes",
    "Ciencias",
    "Economia"
]

# =========================================================
# CURSOS HOTSPOT
# Estos cursos generan alta contención
# =========================================================

cursos_hotspot = [
    "MATE301",
    "PROG202",
    "BD504",
    "MED101",
    "DER300"
]

# =========================================================
# GENERAR ESTUDIANTES
# =========================================================

print("Generando estudiantes...")

estudiantes = pd.DataFrame({
    "student_id": range(1, NUM_ESTUDIANTES + 1),
    "nombre": [fake.name() for _ in range(NUM_ESTUDIANTES)],
    "facultad": np.random.choice(facultades, NUM_ESTUDIANTES),
    "semestre": np.random.randint(1, 11, NUM_ESTUDIANTES),
    "sede": np.random.choice(
        sedes,
        NUM_ESTUDIANTES,
        p=[0.7, 0.1, 0.1, 0.1]
    )
})

# =========================================================
# GENERAR CURSOS
# =========================================================

print("Generando cursos...")

cursos = []

for i in range(NUM_CURSOS):

    if i < len(cursos_hotspot):
        codigo = cursos_hotspot[i]
        cupos = 40
    else:
        codigo = f"CUR{i:03}"
        cupos = random.randint(20, 60)

    cursos.append({
        "course_id": i + 1,
        "codigo_curso": codigo,
        "nombre_curso": f"Curso {codigo}",
        "facultad": random.choice(facultades),
        "cupos_totales": cupos
    })

cursos = pd.DataFrame(cursos)

# =========================================================
# GENERAR INSCRIPCIONES
# =========================================================

print("Generando inscripciones...")

inscripciones = []

fechas = pd.date_range(
    start="2026-01-15 06:00:00",
    end="2026-01-20 22:00:00",
    periods=NUM_INSCRIPCIONES
)

for i in range(NUM_INSCRIPCIONES):

    estudiante = random.randint(1, NUM_ESTUDIANTES)

    # Hotspot:
    # muchos estudiantes intentando entrar
    # al mismo curso
    if random.random() < 0.45:
        curso = random.choice(cursos_hotspot)
    else:
        curso = random.choice(cursos["codigo_curso"].tolist())

    sede = random.choice(sedes)

    # =====================================================
    # SIMULAR RESULTADO OPERACIONAL
    # =====================================================

    prob = random.random()

    if prob < 0.80:
        resultado = "EXITOSA"
    elif prob < 0.90:
        resultado = "CUPO_AGOTADO"
    elif prob < 0.96:
        resultado = "RETRY"
    else:
        resultado = "TIMEOUT"

    # =====================================================
    # LATENCIA
    # =====================================================

    if sede == "Medellin":
        latencia = np.random.normal(120, 30)
    else:
        latencia = np.random.normal(350, 120)

    latencia = max(20, round(latencia, 2))

    inscripciones.append({
        "inscripcion_id": i + 1,
        "student_id": estudiante,
        "codigo_curso": curso,
        "fecha_inscripcion": fechas[i],
        "sede": sede,
        "resultado": resultado,
        "latencia_ms": latencia,
        "hubo_retry": resultado == "RETRY",
        "hubo_timeout": resultado == "TIMEOUT"
    })

inscripciones = pd.DataFrame(inscripciones)

# =========================================================
# GUARDAR PARQUET BRONZE
# =========================================================

print("Guardando archivos Parquet...")

estudiantes.to_parquet(
    BRONZE / "estudiantes.parquet",
    index=False
)

cursos.to_parquet(
    BRONZE / "cursos.parquet",
    index=False
)

inscripciones.to_parquet(
    BRONZE / "inscripciones.parquet",
    index=False
)

# =========================================================
# RESUMEN FINAL
# =========================================================

print("\n====================================")
print("DATOS GENERADOS CORRECTAMENTE")
print("====================================")

print(f"Estudiantes   : {len(estudiantes):,}")
print(f"Cursos        : {len(cursos):,}")
print(f"Inscripciones : {len(inscripciones):,}")

print("\nArchivos creados en:")
print("lakehouse/bronze/")