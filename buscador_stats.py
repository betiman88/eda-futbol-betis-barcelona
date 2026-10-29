
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from pywinauto import Desktop


# ============================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CARPETA_RAW = BASE_DIR / "data" / "raw"
CARPETA_PROCESSED = BASE_DIR / "data" / "processed"

SCRIPT_PREPARAR = BASE_DIR / "src" / "prepare_match.py"
ARCHIVO_POWERBI = BASE_DIR / "Dashboard Barcelona-Betis.pbix"

URL_COMPETICIONES = (
    "https://raw.githubusercontent.com/"
    "statsbomb/open-data/master/data/competitions.json"
)

URL_BASE_PARTIDOS = (
    "https://raw.githubusercontent.com/"
    "statsbomb/open-data/master/data/matches"
)

URL_BASE_EVENTOS = (
    "https://raw.githubusercontent.com/"
    "statsbomb/open-data/master/data/events"
)

CARPETA_RAW.mkdir(parents=True, exist_ok=True)
CARPETA_PROCESSED.mkdir(parents=True, exist_ok=True)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_json(url):
    """Descarga un JSON y devuelve su contenido."""
    respuesta = requests.get(url, timeout=60)
    respuesta.raise_for_status()
    return respuesta.json()


def seleccionar_opcion(df, columna, mensaje):
    """Muestra opciones numeradas y devuelve la fila seleccionada."""
    df = df.reset_index(drop=True)

    print(f"\n{mensaje}")

    for i, valor in enumerate(df[columna].tolist(), start=1):
        print(f"{i}. {valor}")

    while True:
        try:
            opcion = int(input("\nSelecciona una opción: "))

            if 1 <= opcion <= len(df):
                return df.iloc[opcion - 1]

            print("Número fuera de rango.")

        except ValueError:
            print("Introduce un número válido.")


# ============================================================
# SELECCIÓN DE COMPETICIÓN, TEMPORADA Y PARTIDO
# ============================================================

def seleccionar_partido():
    """Permite seleccionar competición, temporada y partido."""

    print("\nDescargando lista de competiciones de StatsBomb...")
    competiciones = obtener_json(URL_COMPETICIONES)

    df_competiciones = pd.DataFrame(competiciones)

    df_competiciones = (
        df_competiciones[
            ["competition_id", "competition_name"]
        ]
        .drop_duplicates()
        .sort_values(
            ["competition_name", "competition_id"]
        )
        .reset_index(drop=True)
    )

    competicion = seleccionar_opcion(
        df_competiciones,
        "competition_name",
        "COMPETICIONES DISPONIBLES"
    )

    competition_id = int(competicion["competition_id"])
    competition_name = competicion["competition_name"]

    temporadas = pd.DataFrame(competiciones)

    temporadas = temporadas[
        temporadas["competition_id"] == competition_id
    ][["season_id", "season_name"]].drop_duplicates()

    temporadas = temporadas.sort_values(
        "season_name"
    ).reset_index(drop=True)

    temporada = seleccionar_opcion(
        temporadas,
        "season_name",
        f"TEMPORADAS DE {competition_name}"
    )

    season_id = int(temporada["season_id"])
    season_name = temporada["season_name"]

    url_partidos = (
        f"{URL_BASE_PARTIDOS}/"
        f"{competition_id}/{season_id}.json"
    )

    print("\nDescargando lista de partidos...")
    partidos = obtener_json(url_partidos)

    if not partidos:
        raise RuntimeError(
            "No se han encontrado partidos para esa temporada."
        )

    df_partidos = pd.json_normalize(partidos)

    columnas_necesarias = [
        "match_id",
        "match_date",
        "home_team.home_team_name",
        "away_team.away_team_name",
    ]

    faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in df_partidos.columns
    ]

    if faltantes:
        raise RuntimeError(
            "La respuesta de StatsBomb no contiene las columnas: "
            + ", ".join(faltantes)
        )

    df_partidos = df_partidos[columnas_necesarias].copy()

    df_partidos = df_partidos.sort_values(
        "match_date",
        ascending=False
    ).reset_index(drop=True)

    df_partidos["partido"] = (
        df_partidos["home_team.home_team_name"]
        + " - "
        + df_partidos["away_team.away_team_name"]
        + " | "
        + df_partidos["match_date"].astype(str)
    )

    partido = seleccionar_opcion(
        df_partidos,
        "partido",
        f"PARTIDOS DE {competition_name} - {season_name}"
    )

    return {
        "competition_id": competition_id,
        "competition_name": competition_name,
        "season_id": season_id,
        "season_name": season_name,
        "match_id": int(partido["match_id"]),
        "match_date": str(partido["match_date"]),
        "home_team": str(
            partido["home_team.home_team_name"]
        ),
        "away_team": str(
            partido["away_team.away_team_name"]
        ),
    }


# ============================================================
# DESCARGA DE EVENTOS Y METADATOS
# ============================================================

def descargar_partido(datos):
    """Descarga los eventos y guarda los metadatos del partido."""

    match_id = datos["match_id"]

    url_eventos = f"{URL_BASE_EVENTOS}/{match_id}.json"

    print(f"\nDescargando eventos del partido {match_id}...")

    eventos = obtener_json(url_eventos)

    archivo_eventos = CARPETA_RAW / f"{match_id}.json"

    with open(archivo_eventos, "w", encoding="utf-8") as archivo:
        json.dump(
            eventos,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    print(f"Eventos guardados en:\n{archivo_eventos}")
    print(f"Número de eventos descargados: {len(eventos)}")

    archivo_metadata = (
        CARPETA_PROCESSED / "partido_actual.json"
    )

    with open(archivo_metadata, "w", encoding="utf-8") as archivo:
        json.dump(
            datos,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    print(f"Metadatos guardados en:\n{archivo_metadata}")


# ============================================================
# GENERAR LOS CSV PARA POWER BI
# ============================================================

def preparar_datos(match_id):
    """Ejecuta prepare_match.py para generar los CSV."""

    if not SCRIPT_PREPARAR.exists():
        raise FileNotFoundError(
            f"No encuentro el script:\n{SCRIPT_PREPARAR}"
        )

    print("\nPreparando los datos para Power BI...")

    resultado = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PREPARAR),
            str(match_id)
        ],
        cwd=str(BASE_DIR),
        check=True
    )

    archivo_eventos = (
        CARPETA_PROCESSED / "eventos_partido.csv"
    )
    archivo_tiros = (
        CARPETA_PROCESSED / "tiros_partido.csv"
    )

    if not archivo_eventos.exists():
        raise FileNotFoundError(
            f"No se ha generado:\n{archivo_eventos}"
        )

    if not archivo_tiros.exists():
        raise FileNotFoundError(
            f"No se ha generado:\n{archivo_tiros}"
        )

    print("\nCSV generados correctamente:")
    print(f"- {archivo_eventos}")
    print(f"- {archivo_tiros}")

    return resultado


# ============================================================
# CONTROL DE POWER BI
# ============================================================

def ventanas_powerbi():
    """Devuelve las ventanas de Power BI Desktop detectadas."""

    ventanas = []

    try:
        escritorio = Desktop(backend="uia")

        for ventana in escritorio.windows():
            try:
                titulo = ventana.window_text().strip()

                if "power bi desktop" in titulo.lower():
                    ventanas.append(ventana)

            except Exception:
                continue

    except Exception as error:
        print(f"Aviso al buscar ventanas: {error}")

    return ventanas


def abrir_powerbi():
    """Abre el informe si es necesario y espera a que cargue."""

    print("\nComprobando Power BI Desktop...")

    ventanas = ventanas_powerbi()

    if ventanas:
        print("Power BI ya está abierto.")
        ventana = ventanas[0]
    else:
        if not ARCHIVO_POWERBI.exists():
            raise FileNotFoundError(
                f"No encuentro el informe Power BI:\n"
                f"{ARCHIVO_POWERBI}"
            )

        print("Abriendo el informe de Power BI...")
        os.startfile(str(ARCHIVO_POWERBI))

        ventana = None
        limite = time.time() + 180

        while time.time() < limite:
            time.sleep(3)
            ventanas = ventanas_powerbi()

            if ventanas:
                ventana = ventanas[0]
                break

        if ventana is None:
            raise RuntimeError(
                "Power BI no ha aparecido en las ventanas "
                "detectadas en 180 segundos. Comprueba si se "
                "ha abierto o si muestra algún diálogo."
            )

    # Dar tiempo a que el informe termine de cargarse.
    try:
        ventana.set_focus()
    except Exception:
        pass

    print("Ventana detectada:")
    print(f"- {ventana.window_text()}")

    time.sleep(10)

    # Buscar de nuevo por si cambió el título al cargar.
    ventanas = ventanas_powerbi()

    if ventanas:
        ventana = ventanas[0]

    return ventana


def buscar_boton_actualizar(ventana):
    """
    Busca Actualizar recorriendo todos los controles accesibles.
    No depende únicamente de que el control sea tipo Button.
    """

    candidatos = []

    try:
        controles = ventana.descendants()
    except Exception:
        controles = []

    for control in controles:
        try:
            nombre = control.window_text().strip().lower()

            if (
                nombre == "actualizar"
                or nombre == "refresh"
                or nombre.startswith("actualizar ")
                or nombre.startswith("refresh ")
            ):
                candidatos.append(control)

        except Exception:
            continue

    return candidatos


def actualizar_powerbi(ventana):
    """Pulsa Actualizar y espera a que Power BI procese los datos."""

    print("\nBuscando el control Actualizar...")

    try:
        ventana.set_focus()
        time.sleep(2)
    except Exception as error:
        print(f"Aviso al activar la ventana: {error}")

    botones = buscar_boton_actualizar(ventana)

    if not botones:
        print(
            "\nNo se ha encontrado el control Actualizar "
            "por su nombre exacto."
        )

        print("\nControles visibles que contienen 'actualizar' "
              "o 'refresh':")

        try:
            for control in ventana.descendants():
                try:
                    nombre = control.window_text().strip()

                    if (
                        "actualizar" in nombre.lower()
                        or "refresh" in nombre.lower()
                    ):
                        print(
                            f"- Texto: {nombre!r} | "
                            f"Tipo: {control.friendly_class_name()}"
                        )
                except Exception:
                    continue
        except Exception:
            pass

        raise RuntimeError(
            "No se ha podido localizar el control Actualizar. "
            "El informe está abierto, pero no se ha confirmado "
            "la actualización automática."
        )

    for i, boton in enumerate(botones, start=1):
        try:
            print(
                f"Control {i}: "
                f"texto={boton.window_text()!r}, "
                f"tipo={boton.friendly_class_name()}"
            )
        except Exception:
            pass

    # Intentar pulsar el primer control encontrado.
    boton = botones[0]

    try:
        boton.click_input()
    except Exception as error:
        raise RuntimeError(
            "Se encontró el control Actualizar, pero no se "
            "pudo pulsar automáticamente."
        ) from error

    print("\nSe ha enviado el clic al control Actualizar.")
    print("Esperando a que Power BI actualice los datos...")

    time.sleep(15)

    print(
        "\nRevisa el informe para confirmar que aparecen "
        "los datos del partido seleccionado y que no hay "
        "mensajes de error."
    )


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def procesar_partido(datos):
    """Ejecuta todo el flujo para el partido seleccionado."""

    descargar_partido(datos)

    preparar_datos(datos["match_id"])

    ventana = abrir_powerbi()

    actualizar_powerbi(ventana)


def main():
    print("=" * 60)
    print("BUSCADOR DE PARTIDOS - STATSBOMB OPEN DATA")
    print("=" * 60)

    try:
        datos = seleccionar_partido()

        print("\nPARTIDO SELECCIONADO")
        print("-" * 40)
        print(f"Competición: {datos['competition_name']}")
        print(f"Temporada:   {datos['season_name']}")
        print(f"Fecha:       {datos['match_date']}")
        print(
            f"Partido:     {datos['home_team']} - "
            f"{datos['away_team']}"
        )
        print(f"Match ID:    {datos['match_id']}")

        confirmar = input(
            "\n¿Quieres descargar y cargar este partido? (s/n): "
        ).strip().lower()

        if confirmar not in ("s", "si", "sí", "y", "yes"):
            print("Operación cancelada.")
            return

        procesar_partido(datos)

        print("\n" + "=" * 60)
        print("PROCESO FINALIZADO")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")

    except requests.RequestException as error:
        print(
            "\nError al conectar con StatsBomb o GitHub:\n"
            f"{error}"
        )

    except subprocess.CalledProcessError as error:
        print(
            "\nHa fallado la preparación de los CSV.\n"
            f"Código de salida: {error.returncode}"
        )

    except Exception as error:
        print(f"\nERROR: {error}")
        raise


if __name__ == "__main__":
    main()
