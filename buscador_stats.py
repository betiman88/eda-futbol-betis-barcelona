
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import requests


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

URL_COMPETICIONES = (
    "https://raw.githubusercontent.com/statsbomb/"
    "open-data/master/data/competitions.json"
)

URL_BASE = (
    "https://raw.githubusercontent.com/statsbomb/"
    "open-data/master/data"
)

# Raíz del proyecto
CARPETA_PROYECTO = Path(__file__).resolve().parent

# Carpetas de datos
CARPETA_RAW = CARPETA_PROYECTO / "data" / "raw"
CARPETA_PROCESADOS = CARPETA_PROYECTO / "data" / "processed"

# Script de preparación
SCRIPT_PREPARAR = (
    CARPETA_PROYECTO / "src" / "prepare_match.py"
)

# Informe de Power BI
ARCHIVO_POWERBI = (
    CARPETA_PROYECTO / "Dashboard Barcelona-Betis.pbix"
)

TIMEOUT = 60


# ============================================================
# 2. SELECCIÓN DE OPCIONES
# ============================================================

def seleccionar_opcion(datos, columna_nombre, columna_id, mensaje):
    """Muestra opciones numeradas y devuelve la seleccionada."""

    if datos.empty:
        raise ValueError("No hay opciones disponibles.")

    for i, (_, fila) in enumerate(datos.iterrows(), start=1):
        print(
            f"{i}. {fila[columna_nombre]} "
            f"(ID: {fila[columna_id]})"
        )

    while True:
        try:
            seleccion = int(input(mensaje))

            if 1 <= seleccion <= len(datos):
                return datos.iloc[seleccion - 1]

            print(f"Introduce un número entre 1 y {len(datos)}.")

        except ValueError:
            print("Introduce un número entero válido.")


# ============================================================
# 3. CARGAR COMPETICIONES Y TEMPORADAS
# ============================================================

def cargar_competiciones():
    """Descarga el catálogo de StatsBomb."""

    respuesta = requests.get(
        URL_COMPETICIONES,
        timeout=TIMEOUT
    )
    respuesta.raise_for_status()

    return pd.DataFrame(respuesta.json())


def elegir_competicion_y_temporada(df):
    """Permite elegir una competición y una temporada."""

    competiciones = (
        df[["competition_id", "competition_name"]]
        .drop_duplicates()
        .sort_values("competition_name")
        .reset_index(drop=True)
        .rename(columns={
            "competition_id": "id",
            "competition_name": "nombre"
        })
    )

    print("\n=== COMPETICIONES DISPONIBLES ===")

    competicion = seleccionar_opcion(
        competiciones,
        "nombre",
        "id",
        "\nSelecciona una competición: "
    )

    temporadas = (
        df.loc[
            df["competition_id"] == competicion["id"],
            ["season_id", "season_name"]
        ]
        .drop_duplicates()
        .sort_values("season_name", ascending=False)
        .reset_index(drop=True)
        .rename(columns={
            "season_id": "id",
            "season_name": "nombre"
        })
    )

    print(f"\n=== TEMPORADAS DE {competicion['nombre']} ===")

    temporada = seleccionar_opcion(
        temporadas,
        "nombre",
        "id",
        "\nSelecciona una temporada: "
    )

    return competicion, temporada


# ============================================================
# 4. CARGAR PARTIDOS
# ============================================================

def cargar_partidos(competition_id, season_id):
    """Descarga los partidos de la temporada seleccionada."""

    url = (
        f"{URL_BASE}/matches/"
        f"{competition_id}/{season_id}.json"
    )

    print("\nDescargando partidos...")

    respuesta = requests.get(url, timeout=TIMEOUT)
    respuesta.raise_for_status()

    return pd.json_normalize(respuesta.json(), sep="_")


# ============================================================
# 5. ELEGIR PARTIDO
# ============================================================

def elegir_partido(partidos):
    """Muestra los partidos y permite seleccionar uno."""

    if partidos.empty:
        return None

    columnas = [
        "match_id",
        "match_date",
        "home_team_home_team_name",
        "away_team_away_team_name",
        "home_score",
        "away_score"
    ]

    faltantes = [
        columna for columna in columnas
        if columna not in partidos.columns
    ]

    if faltantes:
        raise ValueError(
            f"Faltan columnas en los partidos: {faltantes}"
        )

    partidos = (
        partidos[columnas]
        .sort_values("match_date")
        .reset_index(drop=True)
    )

    partidos["nombre"] = partidos.apply(
        lambda fila: (
            f"{fila['match_date']} | "
            f"{fila['home_team_home_team_name']} - "
            f"{fila['away_team_away_team_name']} | "
            f"{fila['home_score']} - {fila['away_score']}"
        ),
        axis=1
    )

    partidos["id"] = partidos["match_id"]

    print(f"\n=== PARTIDOS DISPONIBLES: {len(partidos)} ===")

    return seleccionar_opcion(
        partidos,
        "nombre",
        "id",
        "\nSelecciona un partido: "
    )


# ============================================================
# 6. MOSTRAR PARTIDO
# ============================================================

def mostrar_resultado(partido):
    """Muestra la información del encuentro seleccionado."""

    print("\n=== PARTIDO SELECCIONADO ===")
    print("Fecha:", partido["match_date"])
    print(
        "Encuentro:",
        partido["home_team_home_team_name"],
        "-",
        partido["away_team_away_team_name"]
    )
    print(
        "Resultado:",
        partido["home_score"],
        "-",
        partido["away_score"]
    )
    print("Match ID:", int(partido["match_id"]))


# ============================================================
# 7. DESCARGAR JSON DEL PARTIDO
# ============================================================

def descargar_partido(match_id):
    """Descarga y guarda el JSON original en data/raw."""

    url = f"{URL_BASE}/events/{match_id}.json"

    print("\nDescargando eventos del partido...")

    respuesta = requests.get(url, timeout=TIMEOUT)
    respuesta.raise_for_status()

    datos = respuesta.json()

    if not datos:
        raise ValueError(
            "El partido no contiene eventos disponibles."
        )

    CARPETA_RAW.mkdir(parents=True, exist_ok=True)

    ruta_json = CARPETA_RAW / f"{match_id}.json"

    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False)

    print(f"Eventos descargados: {len(datos)}")
    print(f"JSON guardado en: {ruta_json}")

    return ruta_json


# ============================================================
# 8. PREPARAR CSV PARA POWER BI
# ============================================================

def preparar_datos_powerbi(match_id):
    """Ejecuta prepare_match.py con el ID elegido."""

    if not SCRIPT_PREPARAR.exists():
        raise FileNotFoundError(
            f"No se encuentra el script: {SCRIPT_PREPARAR}"
        )

    print("\nGenerando los CSV para Power BI...")

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PREPARAR),
            str(match_id)
        ],
        cwd=str(CARPETA_PROYECTO),
        check=True
    )

    csv_eventos = (
        CARPETA_PROCESADOS / "eventos_partido.csv"
    )
    csv_tiros = (
        CARPETA_PROCESADOS / "tiros_partido.csv"
    )

    if not csv_eventos.exists() or not csv_tiros.exists():
        raise FileNotFoundError(
            "No se han encontrado los dos CSV esperados."
        )

    print("\nCSV generados correctamente:")
    print(csv_eventos)
    print(csv_tiros)


# ============================================================
# 9. ABRIR POWER BI
# ============================================================

def abrir_powerbi():
    """Abre el archivo PBIX con la aplicación asociada en Windows."""

    if not ARCHIVO_POWERBI.exists():
        raise FileNotFoundError(
            f"No se encuentra el informe: {ARCHIVO_POWERBI}"
        )

    print("\nAbriendo el informe de Power BI...")
    os.startfile(str(ARCHIVO_POWERBI))


# ============================================================
# 10. PROCESAR PARTIDO COMPLETO
# ============================================================

def procesar_partido(match_id):
    """
    Coordina descarga, transformación y apertura del informe.
    Esta función también podrá reutilizarse desde la futura GUI.
    """

    descargar_partido(match_id)
    preparar_datos_powerbi(match_id)
    abrir_powerbi()


# ============================================================
# 11. PROGRAMA PRINCIPAL
# ============================================================

def main():
    """Ejecuta el buscador desde la terminal."""

    try:
        df = cargar_competiciones()

        competicion, temporada = (
            elegir_competicion_y_temporada(df)
        )

        partidos = cargar_partidos(
            competicion["id"],
            temporada["id"]
        )

        if partidos.empty:
            print("No hay partidos disponibles.")
            return

        partido = elegir_partido(partidos)

        if partido is None:
            print("No se ha seleccionado ningún partido.")
            return

        mostrar_resultado(partido)

        match_id = int(partido["match_id"])

        procesar_partido(match_id)

        print(
            "\nProceso finalizado. "
            "Si el informe ya estaba abierto, "
            "puede ser necesario actualizarlo."
        )

    except requests.RequestException as error:
        print(f"\nError de conexión o descarga: {error}")

    except subprocess.CalledProcessError as error:
        print(
            "\nError al preparar los datos. "
            f"Código de salida: {error.returncode}"
        )

    except (
        KeyError,
        ValueError,
        FileNotFoundError
    ) as error:
        print(f"\nError durante la ejecución: {error}")


if __name__ == "__main__":
    main()
