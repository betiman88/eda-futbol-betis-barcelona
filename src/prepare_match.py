
import json
from pathlib import Path

import pandas as pd


# ==================================================
# 1. LOCALIZAR Y CARGAR LOS DATOS
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = PROJECT_DIR / "data" / "raw" / "3773631.json"

with open(JSON_PATH, "r", encoding="utf-8") as file:
    events = json.load(file)

df = pd.json_normalize(events)


# ==================================================
# 2. DIAGNÓSTICO INICIAL
# ==================================================

print("=" * 50)
print("ANÁLISIS DEL PARTIDO: BETIS - BARCELONA")
print("=" * 50)

print(f"\nNúmero de eventos: {df.shape[0]}")
print(f"Número de columnas: {df.shape[1]}")

print("\nPrimeros 5 eventos:")
print(
    df[["minute", "type.name", "team.name", "player.name"]].head()
)

print("\nValores nulos: las 15 columnas con más nulos")
print(df.isna().sum().sort_values(ascending=False).head(15))


# ==================================================
# 3. AUDITORÍA DE EVENTOS
# ==================================================

print("\n" + "=" * 50)
print("AUDITORÍA DE LOS EVENTOS")
print("=" * 50)

print("\nEventos por tipo:")
print(df["type.name"].value_counts(dropna=False).to_string())

print("\nEventos por equipo:")
print(df["team.name"].value_counts(dropna=False).to_string())


# ==================================================
# 4. ANÁLISIS DE LOS TIROS
# ==================================================

shots = df[df["type.name"] == "Shot"].copy()

print("\nNúmero total de tiros:", len(shots))

print("\nTiros por equipo:")
print(shots["team.name"].value_counts().to_string())

print("\nResultados de los tiros:")
print(shots["shot.outcome.name"].value_counts(dropna=False).to_string())

print("\nDetalle de los tiros:")
print(
    shots[
        [
            "minute",
            "team.name",
            "player.name",
            "shot.statsbomb_xg",
            "shot.outcome.name",
        ]
    ].to_string(index=False)
)


# ==================================================
# 5. VALIDACIÓN DE LOS GOLES
# ==================================================

print("\n" + "=" * 50)
print("VALIDACIÓN DEL MARCADOR")
print("=" * 50)

# Goles registrados como tiros
goals = shots[shots["shot.outcome.name"] == "Goal"]

print("\nGoles registrados en eventos de tiro:")
print(
    goals[["minute", "team.name", "player.name"]].to_string(index=False)
)

# Eventos de gol propio
own_goals = df[
    df["type.name"].isin(["Own Goal For", "Own Goal Against"])
]

columns_to_show = [
    "minute",
    "type.name",
    "team.name",
    "player.name",
]

print("\nEventos de gol propio:")

if own_goals.empty:
    print("No se han encontrado eventos de gol propio.")
else:
    print(own_goals[columns_to_show].to_string(index=False))


# ==================================================
# 6. RESUMEN DE TIROS Y GOLES ESPERADOS (xG)
# ==================================================

print("\nResumen por equipo:")

summary = shots.groupby("team.name").agg(
    tiros=("id", "count"),
    goles_en_tiros=(
        "shot.outcome.name",
        lambda s: (s == "Goal").sum(),
    ),
    xG=("shot.statsbomb_xg", "sum"),
)

print(summary.round(3).to_string())

print("\nNúmero de eventos de gol propio:")
print("Own Goal For:", (df["type.name"] == "Own Goal For").sum())
print("Own Goal Against:", (df["type.name"] == "Own Goal Against").sum())

# ==================================================
# 7. PREPARACIÓN Y EXPORTACIÓN DE DATOS
# ==================================================

print("\n" + "=" * 50)
print("EXPORTACIÓN DE DATOS PARA POWER BI")
print("=" * 50)

OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Función auxiliar para separar las coordenadas [x, y]
def extract_coordinates(series, axis):
    return series.apply(
        lambda value: (
            value[axis]
            if isinstance(value, list) and len(value) > axis
            else None
        )
    )


# 1. Tabla general de eventos
event_columns = [
    "id",
    "index",
    "period",
    "minute",
    "second",
    "timestamp",
    "type.name",
    "team.name",
    "possession_team.name",
    "player.name",
    "possession",
    "play_pattern.name",
    "location",
    "pass.end_location",
    "shot.end_location",
    "shot.statsbomb_xg",
    "shot.outcome.name",
]

# Conservar únicamente las columnas disponibles
event_columns = [col for col in event_columns if col in df.columns]

events_export = df[event_columns].copy()

# Coordenadas de inicio de cada evento
if "location" in events_export.columns:
    events_export["x"] = extract_coordinates(events_export["location"], 0)
    events_export["y"] = extract_coordinates(events_export["location"], 1)
    events_export = events_export.drop(columns=["location"])

# Coordenadas de finalización del pase
if "pass.end_location" in events_export.columns:
    events_export["pass_end_x"] = extract_coordinates(
        events_export["pass.end_location"], 0
    )
    events_export["pass_end_y"] = extract_coordinates(
        events_export["pass.end_location"], 1
    )
    events_export = events_export.drop(columns=["pass.end_location"])

# Coordenadas finales del tiro
if "shot.end_location" in events_export.columns:
    events_export["shot_end_x"] = extract_coordinates(
        events_export["shot.end_location"], 0
    )
    events_export["shot_end_y"] = extract_coordinates(
        events_export["shot.end_location"], 1
    )
    events_export = events_export.drop(columns=["shot.end_location"])

events_path = OUTPUT_DIR / "eventos_partido.csv"
events_export.to_csv(events_path, index=False, encoding="utf-8-sig")


# 2. Tabla específica de tiros
shot_columns = [
    "id",
    "index",
    "period",
    "minute",
    "second",
    "team.name",
    "player.name",
    "location",
    "shot.end_location",
    "shot.statsbomb_xg",
    "shot.outcome.name",
    "shot.body_part.name",
    "shot.type.name",
    "shot.technique.name",
    "shot.first_time",
    "shot.one_on_one",
]

shot_columns = [col for col in shot_columns if col in shots.columns]
shots_export = shots[shot_columns].copy()

# Coordenadas de origen y finalización
for source_column, prefix in [
    ("location", "shot"),
    ("shot.end_location", "end"),
]:
    if source_column in shots_export.columns:
        shots_export[f"{prefix}_x"] = extract_coordinates(
            shots_export[source_column], 0
        )
        shots_export[f"{prefix}_y"] = extract_coordinates(
            shots_export[source_column], 1
        )
        shots_export = shots_export.drop(columns=[source_column])

# Nombres más cómodos para Power BI
shots_export = shots_export.rename(
    columns={
        "team.name": "equipo",
        "player.name": "jugador",
        "shot.statsbomb_xg": "xg",
        "shot.outcome.name": "resultado",
        "shot.body_part.name": "parte_cuerpo",
        "shot.type.name": "tipo_tiro",
        "shot.technique.name": "tecnica",
        "shot.first_time": "primer_toque",
        "shot.one_on_one": "mano_a_mano",
        "minute": "minuto",
        "second": "segundo",
        "period": "periodo",
    }
)

shots_path = OUTPUT_DIR / "tiros_partido.csv"
shots_export.to_csv(shots_path, index=False, encoding="utf-8-sig")


# 3. Confirmar que los archivos se han creado
print(f"\nEventos exportados: {len(events_export)}")
print(f"Columnas de eventos: {len(events_export.columns)}")
print(f"Archivo: {events_path}")

print(f"\nTiros exportados: {len(shots_export)}")
print(f"Columnas de tiros: {len(shots_export.columns)}")
print(f"Archivo: {shots_path}")

print("\nColumnas disponibles en la tabla de tiros:")
print(shots_export.columns.tolist())

print("\nPrimeros tiros exportados:")
print(shots_export.head().to_string(index=False))