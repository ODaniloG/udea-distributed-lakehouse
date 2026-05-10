import pandas as pd
from pathlib import Path

# =========================================================
# RUTAS DEL LAKEHOUSE
# =========================================================

BRONZE = Path("lakehouse/bronze")
SILVER = Path("lakehouse/silver")
DOCS = Path("docs")

SILVER.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

# =========================================================
# LEER DATOS BRONZE
# =========================================================

print("Leyendo datos Bronze...")

estudiantes_raw = pd.read_parquet(BRONZE / "estudiantes.parquet")
cursos_raw = pd.read_parquet(BRONZE / "cursos.parquet")
inscripciones_raw = pd.read_parquet(BRONZE / "inscripciones.parquet")

# =========================================================
# COPIAS DE TRABAJO
# =========================================================

estudiantes = estudiantes_raw.copy()
cursos = cursos_raw.copy()
inscripciones = inscripciones_raw.copy()

# =========================================================
# LIMPIEZA DE ESTUDIANTES
# =========================================================

print("Limpiando estudiantes...")

estudiantes["student_id"] = estudiantes["student_id"].astype(int)
estudiantes["nombre"] = estudiantes["nombre"].astype(str).str.strip()
estudiantes["facultad"] = estudiantes["facultad"].astype(str).str.strip()
estudiantes["semestre"] = estudiantes["semestre"].astype(int)
estudiantes["sede"] = estudiantes["sede"].astype(str).str.strip()

estudiantes = estudiantes.drop_duplicates(subset=["student_id"])

# =========================================================
# LIMPIEZA DE CURSOS
# =========================================================

print("Limpiando cursos...")

cursos["course_id"] = cursos["course_id"].astype(int)
cursos["codigo_curso"] = cursos["codigo_curso"].astype(str).str.strip()
cursos["nombre_curso"] = cursos["nombre_curso"].astype(str).str.strip()
cursos["facultad"] = cursos["facultad"].astype(str).str.strip()
cursos["cupos_totales"] = cursos["cupos_totales"].astype(int)

cursos = cursos.drop_duplicates(subset=["codigo_curso"])

# =========================================================
# LIMPIEZA DE INSCRIPCIONES
# =========================================================

print("Limpiando inscripciones...")

inscripciones["inscripcion_id"] = inscripciones["inscripcion_id"].astype(int)
inscripciones["student_id"] = inscripciones["student_id"].astype(int)
inscripciones["codigo_curso"] = inscripciones["codigo_curso"].astype(str).str.strip()
inscripciones["fecha_inscripcion"] = pd.to_datetime(inscripciones["fecha_inscripcion"])
inscripciones["sede"] = inscripciones["sede"].astype(str).str.strip()
inscripciones["resultado"] = inscripciones["resultado"].astype(str).str.strip()
inscripciones["latencia_ms"] = pd.to_numeric(inscripciones["latencia_ms"], errors="coerce")
inscripciones["hubo_retry"] = inscripciones["hubo_retry"].astype(bool)
inscripciones["hubo_timeout"] = inscripciones["hubo_timeout"].astype(bool)

# Eliminar filas inválidas críticas
inscripciones = inscripciones.dropna(
    subset=[
        "inscripcion_id",
        "student_id",
        "codigo_curso",
        "fecha_inscripcion",
        "resultado",
        "latencia_ms"
    ]
)

inscripciones = inscripciones.drop_duplicates(subset=["inscripcion_id"])

# =========================================================
# VALIDACIONES DE CALIDAD
# =========================================================

print("Generando reporte de calidad...")

reporte = []

reporte.append("REPORTE DE CALIDAD - ZONA SILVER")
reporte.append("=================================")
reporte.append("")
reporte.append("1. Filas originales Bronze vs Silver")
reporte.append("------------------------------------")
reporte.append(f"Estudiantes Bronze   : {len(estudiantes_raw):,}")
reporte.append(f"Estudiantes Silver   : {len(estudiantes):,}")
reporte.append(f"Cursos Bronze        : {len(cursos_raw):,}")
reporte.append(f"Cursos Silver        : {len(cursos):,}")
reporte.append(f"Inscripciones Bronze : {len(inscripciones_raw):,}")
reporte.append(f"Inscripciones Silver : {len(inscripciones):,}")
reporte.append("")
reporte.append("2. Nulos por tabla Silver")
reporte.append("-------------------------")
reporte.append("Estudiantes:")
reporte.append(str(estudiantes.isnull().sum()))
reporte.append("")
reporte.append("Cursos:")
reporte.append(str(cursos.isnull().sum()))
reporte.append("")
reporte.append("Inscripciones:")
reporte.append(str(inscripciones.isnull().sum()))
reporte.append("")
reporte.append("3. Distribucion de resultados de inscripcion")
reporte.append("--------------------------------------------")
reporte.append(str(inscripciones["resultado"].value_counts()))
reporte.append("")
reporte.append("4. Latencia")
reporte.append("-----------")
reporte.append(f"Latencia minima ms   : {inscripciones['latencia_ms'].min():.2f}")
reporte.append(f"Latencia promedio ms : {inscripciones['latencia_ms'].mean():.2f}")
reporte.append(f"Latencia maxima ms   : {inscripciones['latencia_ms'].max():.2f}")
reporte.append("")
reporte.append("5. Rango temporal")
reporte.append("-----------------")
reporte.append(f"Fecha minima : {inscripciones['fecha_inscripcion'].min()}")
reporte.append(f"Fecha maxima : {inscripciones['fecha_inscripcion'].max()}")

# Guardar reporte en docs
with open(DOCS / "reporte_calidad_silver.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(reporte))

# =========================================================
# GUARDAR DATOS SILVER
# =========================================================

print("Guardando archivos Silver...")

estudiantes.to_parquet(SILVER / "estudiantes_silver.parquet", index=False)
cursos.to_parquet(SILVER / "cursos_silver.parquet", index=False)
inscripciones.to_parquet(SILVER / "inscripciones_silver.parquet", index=False)

print("\n====================================")
print("ZONA SILVER GENERADA CORRECTAMENTE")
print("====================================")
print(f"Estudiantes Silver   : {len(estudiantes):,}")
print(f"Cursos Silver        : {len(cursos):,}")
print(f"Inscripciones Silver : {len(inscripciones):,}")
print("")
print("Archivos creados en:")
print("lakehouse/silver/")
print("")
print("Reporte creado en:")
print("docs/reporte_calidad_silver.txt")