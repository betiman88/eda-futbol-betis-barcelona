⚽ Análisis de datos de fútbol con Python y Power BI

📌 Descripción del proyecto

Proyecto de análisis de datos de fútbol basado en StatsBomb Open Data, desarrollado con Python y Power BI.

El objetivo es construir un flujo de trabajo que permita seleccionar un partido de fútbol, descargar sus eventos, procesar la información y generar datasets preparados para su análisis y visualización en Power BI.

El proyecto comenzó como un análisis exploratorio de un partido entre el Real Betis y el FC Barcelona, y ha evolucionado hacia un proceso reutilizable para analizar diferentes encuentros disponibles en StatsBomb Open Data.

Actualmente, el flujo de trabajo permite seleccionar una competición, una temporada y un partido, descargar sus eventos y generar archivos CSV con información estructurada para Power BI.

🎯 Objetivos

Trabajar con datos reales de fútbol procedentes de una fuente de datos abierta.

Practicar la extracción y transformación de datos con Python.

Procesar datos estructurados en formato JSON.

Limpiar, organizar y transformar eventos futbolísticos.

Preparar datasets para su utilización en herramientas de Business Intelligence.

Crear visualizaciones e indicadores mediante Power BI.

Automatizar progresivamente el flujo de trabajo desde la selección del partido hasta la actualización del informe.

🛠️ Tecnologías utilizadas

Tecnología

Uso

Python

Automatización y procesamiento de datos

Pandas

Manipulación y transformación de datos

Requests

Descarga de datos desde GitHub

JSON

Almacenamiento de los datos originales y metadatos

CSV

Exportación de los datasets procesados

Power BI Desktop

Visualización y análisis de los datos

Pywinauto

Automatización de la interfaz de Power BI

Git y GitHub

Control de versiones y documentación del proyecto

🔄 Flujo de trabajo

El proyecto sigue un flujo inspirado en un proceso ETL (Extract, Transform, Load).

Extracción: consulta de las competiciones, temporadas y partidos disponibles en StatsBomb Open Data.

Selección: elección del encuentro que se quiere analizar.

Descarga: obtención de los eventos del partido en formato JSON.

Transformación: procesamiento de los eventos mediante Python y Pandas.

Exportación: generación de archivos CSV preparados para Power BI.

Visualización: análisis de los datos mediante un informe de Power BI.

Actualización: automatización de la apertura y actualización del informe, actualmente en desarrollo.

📂 Estructura del proyecto

eda-futbol-betis-barcelona/
│
├── buscador_stats.py
│
├── src/
│   └── prepare_match.py
│
├── data/
│   ├── raw/
│   │   └── {match_id}.json
│   │
│   └── processed/
│       ├── eventos_partido.csv
│       ├── tiros_partido.csv
│       └── partido_actual.json
│
├── Dashboard Barcelona-Betis.pbix
│
├── .gitignore
├── requirements.txt
└── README.md

La estructura representa la organización del proyecto. Los archivos de datos se generan durante la ejecución y pueden estar excluidos del repositorio mediante .gitignore.

📊 Datos generados

eventos_partido.csv

Contiene los eventos del encuentro procesados para facilitar su análisis.

tiros_partido.csv

Contiene información específica de los disparos, incluyendo, entre otros campos:

Equipo y jugador.

Minuto y segundo.

Goles esperados (xG).

Resultado del disparo.

Parte del cuerpo y técnica.

Coordenadas del disparo y de su destino.

Indicadores de primer toque y mano a mano, cuando están disponibles.

partido_actual.json

Guarda los metadatos del encuentro seleccionado, como la competición, la temporada, la fecha, los equipos y el identificador del partido.

📈 Power BI

El proyecto incluye un informe de Power BI para explorar los datos del encuentro y visualizar información futbolística.

Los CSV se generan en rutas fijas para mantener la compatibilidad con las consultas del informe al cambiar de partido.

La actualización automática del informe desde Python está en desarrollo. La descarga y preparación de los datos funcionan; queda terminar de automatizar la interacción con Power BI Desktop y comprobar que la actualización se completa correctamente.

🚀 Instalación y ejecución

Requisitos

Python instalado.

Power BI Desktop.

Git.

Acceso a Internet para descargar los datos de StatsBomb.

1. Clonar el repositorio

git clone <URL_DEL_REPOSITORIO>
cd eda-futbol-betis-barcelona

2. Crear un entorno virtual

En Windows, desde la terminal del proyecto:

python -m venv venv

Activar el entorno virtual en PowerShell:

.\venv\Scripts\Activate.ps1

Si PowerShell bloquea la ejecución del script de activación, se puede utilizar temporalmente:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1

3. Instalar las dependencias

Si el repositorio contiene requirements.txt:

pip install -r requirements.txt

4. Ejecutar el buscador

python buscador_stats.py

El programa permite seleccionar la competición, la temporada y el partido. Tras confirmar la selección, descarga los datos y ejecuta el procesamiento para generar los CSV.

A continuación, intenta abrir el informe de Power BI y automatizar su actualización.

📚 Fuente de datos

Los datos se obtienen de StatsBomb Open Data:

https://github.com/statsbomb/open-data

La disponibilidad de competiciones, temporadas y partidos depende de los datos publicados por StatsBomb.

🔧 Próximas mejoras

Completar y validar la actualización automática del informe de Power BI.

Mejorar la gestión de errores y los tiempos de carga.

Incorporar nuevas métricas e indicadores de rendimiento futbolístico.

Ampliar el análisis a más partidos y temporadas.

Documentar las transformaciones aplicadas a los datos.

Mejorar la configuración del proyecto para facilitar su ejecución en otros equipos.

👨‍💻 Autor

Proyecto personal de aprendizaje y desarrollo de competencias en análisis de datos, Python, procesamiento de datos y Business Intelligence.