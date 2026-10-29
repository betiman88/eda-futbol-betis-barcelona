
import json
import sys
from pathlib import Path

import pandas as pd


# ============================================================
# 1. CONFIGURACIÓN Y CARGA DE DATOS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

# Recibir el ID desde buscador_stats.py.
# Si se ejecuta manualmente sin argumentos, usar el partido
# de ejemplo original.
MATCH_ID = sys.argv[1] if len(sys.argv) > 1 else "3773631"

JSON_PATH = PROJECT_DIR / "data" / "raw" / f"{MATCH_ID}.json"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

if not JSON_PATH.exists():
    raise FileNotFoundError(
        f"No se encuentra el JSON del partido: {JSON_PATH}"
    )

with open(JSON_PATH, "r", encoding="utf-8") as file:
    events = json.load(file)

if not events:
    raise ValueError(
        f"El partido {MATCH_ID} no contiene eventos."
    )

df = pd.json_normalize(events, sep=".")

print("=" * 60)
print(f"ANÁLISIS DEL PARTIDO: ID {MATCH_ID}")
print("=" * 60)

print(f"\nNúmero de eventos: {df.shape[0]}")
print(f"Número de columnas: {df.shape[1]}")

columnas_diagnostico = [
    "minute",
    "type.name",
    "team.name",
    "player.name",
]
columnas_diagnostico = [
    columna for columna in columnas_diagnostico
    if columna in df.columns
]

print("\nPrimeros 5 eventos:")
print(df[columnas_diagnostico].head())

print("\nColumnas con más valores nulos:")
print(
    df.isna()
    .sum()
    .sort_values(ascending=False)
    .head(15)
)


# ============================================================
# 2. AUDITORÍA DE EVENTOS
# ============================================================

print("\n" + "=" * 60)
print("AUDITORÍA DE EVENTOS")
print("=" * 60)

if "type.name" in df.columns:
    print("\nEventos por tipo:")
    print(
        df["type.name"]
        .value_counts(dropna=False)
        .to_string()
    )

if "team.name" in df.columns:
    print("\nEventos por equipo:")
    print(
        df["team.name"]
        .value_counts(dropna=False)
        .to_string()
    )


# ============================================================
# 3. ANÁLISIS DE LOS TIROS
# ============================================================

if "type.name" not in df.columns:
    raise ValueError(
        "El JSON no contiene la columna 'type.name'."
    )

shots = df[df["type.name"] == "Shot"].copy()

print("\n" + "=" * 60)
print("ANÁLISIS DE TIROS")
print("=" * 60)

print(f"\nNúmero total de tiros: {len(shots)}")

if "team.name" in shots.columns:
    print("\nTiros por equipo:")
    print(shots["team.name"].value_counts().to_string())

if "shot.outcome.name" in shots.columns:
    print("\nResultados de los tiros:")
    print(
        shots["shot.outcome.name"]
        .value_counts(dropna=False)
        .to_string()
    )

columnas_detalle = [
    "minute",
    "team.name",
    "player.name",
    "shot.statsbomb_xg",
    "shot.outcome.name",
]
columnas_detalle = [
    columna for columna in columnas_detalle
    if columna in shots.columns
]

print("\nDetalle de los tiros:")
print(shots[columnas_detalle].to_string(index=False))


# ============================================================
# 4. VALIDACIÓN DE GOLES
# ============================================================

print("\n" + "=" * 60)
print("VALIDACIÓN DE GOLES")
print("=" * 60)

if "shot.outcome.name" in shots.columns:
    goals = shots[
        shots["shot.outcome.name"] == "Goal"
    ].copy()

    columnas_goles = [
        "minute",
        "team.name",
        "player.name",
    ]
    columnas_goles = [
        columna for columna in columnas_goles
        if columna in goals.columns
    ]

    print("\nGoles registrados en eventos de tiro:")
    print(goals[columnas_goles].to_string(index=False))
else:
    print(
        "\nNo se encuentra la columna "
        "'shot.outcome.name'."
    )

if "type.name" in df.columns:
    own_goals = df[
        df["type.name"].isin(
            ["Own Goal For", "Own Goal Against"]
        )
    ]

    columnas_gol_propio = [
        "minute",
        "type.name",
        "team.name",
        "player.name",
    ]
    columnas_gol_propio = [
        columna for columna in columnas_gol_propio
        if columna in own_goals.columns
    ]

    print("\nEventos de gol propio:")

    if own_goals.empty:
        print("No se han encontrado eventos de gol propio.")
    else:
        print(
            own_goals[columnas_gol_propio]
            .to_string(index=False)
        )


# ============================================================
# 5. RESUMEN DE TIROS Y xG
# ============================================================

print("\n" + "=" * 60)
print("RESUMEN DE TIROS Y xG")
print("=" * 60)

if not shots.empty and "team.name" in shots.columns:
    agregaciones = {}

    if "id" in shots.columns:
        agregaciones["tiros"] = ("id", "count")
    else:
        agregaciones["tiros"] = ("team.name", "size")

    if "shot.outcome.name" in shots.columns:
        agregaciones["goles_en_tiros"] = (
            "shot.outcome.name",
            lambda serie: (serie == "Goal").sum(),
        )

    if "shot.statsbomb_xg" in shots.columns:
        agregaciones["xG"] = (
            "shot.statsbomb_xg",
            "sum",
        )

    resumen = shots.groupby("team.name").agg(**agregaciones)

    print(resumen.round(3).to_string())
else:
    print("No hay tiros disponibles para resumir.")

if "type.name" in df.columns:
    print("\nEventos de gol propio:")
    print(
        "Own Goal For:",
        (df["type.name"] == "Own Goal For").sum()
    )
    print(
        "Own Goal Against:",
        (df["type.name"] == "Own Goal Against").sum()
    )


# ============================================================
# 6. FUNCIONES AUXILIARES
# ============================================================

def extract_coordinates(series, axis):
    """Extrae la coordenada X o Y de una lista [x, y]."""

    return series.apply(
        lambda value: (
            value[axis]
            if isinstance(value, list)
            and len(value) > axis
            else None
        )
    )


# ============================================================
# 7. PREPARAR Y EXPORTAR EVENTOS
# ============================================================

print("\n" + "=" * 60)
print("EXPORTACIÓN PARA POWER BI")
print("=" * 60)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

event_columns = [
    columna for columna in event_columns
    if columna in df.columns
]

events_export = df[event_columns].copy()

# Coordenadas iniciales de los eventos.
if "location" in events_export.columns:
    events_export["x"] = extract_coordinates(
        events_export["location"], 0
    )
    events_export["y"] = extract_coordinates(
        events_export["location"], 1
    )

    events_export = events_export.drop(
        columns=["location"]
    )

# Coordenadas finales de los pases.
if "pass.end_location" in events_export.columns:
    events_export["pass_end_x"] = extract_coordinates(
        events_export["pass.end_location"], 0
    )
    events_export["pass_end_y"] = extract_coordinates(
        events_export["pass.end_location"], 1
    )

    events_export = events_export.drop(
        columns=["pass.end_location"]
    )

# Coordenadas finales de los tiros.
if "shot.end_location" in events_export.columns:
    events_export["shot_end_x"] = extract_coordinates(
        events_export["shot.end_location"], 0
    )
    events_export["shot_end_y"] = extract_coordinates(
        events_export["shot.end_location"], 1
    )

    events_export = events_export.drop(
        columns=["shot.end_location"]
    )

events_path = OUTPUT_DIR / "eventos_partido.csv"

events_export.to_csv(
    events_path,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 8. PREPARAR Y EXPORTAR TIROS
# ============================================================

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

shot_columns = [
    columna for columna in shot_columns
    if columna in shots.columns
]

shots_export = shots[shot_columns].copy()

# Coordenadas de origen y finalización de cada tiro.
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

        shots_export = shots_export.drop(
            columns=[source_column]
        )

# Nombres de columnas compatibles con Power BI.
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

shots_export.to_csv(
    shots_path,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 9. RESUMEN FINAL DE LA EXPORTACIÓN
# ============================================================

print("\n" + "=" * 60)
print("EXPORTACIÓN COMPLETADA")
print("=" * 60)

print(f"\nPartido procesado: {MATCH_ID}")

print(f"\nEventos exportados: {len(events_export)}")
print(
    f"Columnas de eventos: {len(events_export.columns)}"
)
print(f"Archivo: {events_path.resolve()}")

print(f"\nTiros exportados: {len(shots_export)}")
print(
    f"Columnas de tiros: {len(shots_export.columns)}"
)
print(f"Archivo: {shots_path.resolve()}")

print("\nColumnas de la tabla de tiros:")
print(shots_export.columns.tolist())

print("\nPrimeros tiros exportados:")
print(shots_export.head().to_string(index=False))

print("\nPreparación de datos finalizada correctamente.")
