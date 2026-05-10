import subprocess
import sys
import time

PASOS = [
    ("Generacion de datos Bronze", "scripts/generate_data.py"),
    ("Transformacion Silver", "scripts/transform_silver.py"),
    ("Modelo dimensional Gold", "scripts/transform_gold.py"),
    ("Consultas analiticas", "scripts/analyze.py"),
    ("Benchmark", "scripts/benchmark.py"),
]

print("=" * 60)
print("MINI-LAKEHOUSE UDEA - PIPELINE COMPLETO")
print("=" * 60)

inicio_total = time.time()

for nombre, script in PASOS:
    print(f"\n>>> Ejecutando: {nombre}")
    inicio = time.time()

    resultado = subprocess.run([sys.executable, script])

    if resultado.returncode != 0:
        print(f"ERROR ejecutando {script}")
        sys.exit(1)

    print(f"Completado en {time.time() - inicio:.2f} segundos")

print("\n" + "=" * 60)
print("PIPELINE FINALIZADO CORRECTAMENTE")
print("=" * 60)
print(f"Tiempo total: {time.time() - inicio_total:.2f} segundos")
print("")
print("Revisa las carpetas:")
print("- lakehouse/bronze")
print("- lakehouse/silver")
print("- lakehouse/gold")
print("- docs")