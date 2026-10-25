⚽ Análisis Exploratorio de Datos (EDA) — Real Betis vs FC Barcelona

Proyecto de análisis exploratorio de datos de un partido de fútbol mediante Python, Pandas, Matplotlib y Power BI. El objetivo es explorar la distribución espacial de los eventos del partido y construir visualizaciones que permitan identificar patrones de actividad en el terreno de juego.

🎯 Objetivos del proyecto

Explorar y preparar datos de eventos de un partido de fútbol.

Analizar la distribución espacial de las acciones sobre el terreno de juego.

Crear un mapa de calor para identificar las zonas con mayor concentración de eventos.

Desarrollar un dashboard interactivo en Power BI.

Permitir el análisis por equipo y jugador mediante segmentadores.

Practicar técnicas de análisis exploratorio de datos (EDA) y visualización.

🛠️ Tecnologías utilizadas

Python — preparación y tratamiento de datos.

Pandas — limpieza y manipulación de datos.

NumPy — herramientas para operaciones numéricas.

Matplotlib — creación de gráficos y mapas de calor.

Jupyter Notebook — entorno de análisis.

Power BI Desktop — visualización interactiva y exploración de resultados.

Git y GitHub — control de versiones y publicación del proyecto.

📊 Visualización y análisis

El proyecto incluye un dashboard de Power BI con un mapa de calor de los eventos del partido.

El mapa representa las coordenadas de los eventos sobre un campo de fútbol y utiliza un gradiente de color para mostrar su concentración espacial:

🔵 Azul claro: menor concentración de eventos.

🟡 Amarillo: concentración intermedia.

🔴 Rojo: mayor concentración de eventos.

El dashboard incorpora segmentadores para explorar los datos por equipo y jugador. También permite filtrar por tipo de acción cuando ese campo está disponible en el visual.

El mapa de calor muestra la frecuencia de eventos por zona, no la calidad o la peligrosidad de las acciones.

🗂️ Estructura del proyecto

Datos futbol/
│
├── data/
│   ├── raw/                 # Datos originales
│   └── processed/           # Datos preparados para el análisis
│
├── src/
│   └── prepare_match.py     # Preparación de los datos del partido
│
├── reports/
│   └──                      # Material adicional del proyecto
│
├── analisis.ipynb           # Notebook de análisis exploratorio
├── Dashboard Barcelona-Betis.pbix
├── CampoFutbol_fondo_cesped_web-futbol.jpg
├── guia_proceso_analisis_futbol_python_powerbi.pdf
├── .gitignore
└── README.md

La estructura refleja la organización prevista del proyecto. El contenido concreto de las carpetas puede variar según los archivos incluidos en el repositorio.

🚀 Cómo utilizar el proyecto

1. Clonar el repositorio

git clone URL_DE_TU_REPOSITORIO
cd "Datos futbol"

Sustituye URL_DE_TU_REPOSITORIO por la dirección real del repositorio de GitHub.

2. Preparar el entorno de Python

Es recomendable utilizar un entorno virtual:

python -m venv venv

En Windows, activa el entorno desde PowerShell:

.\venv\Scripts\Activate.ps1

Instala las librerías necesarias:

python -m pip install pandas numpy matplotlib jupyter

3. Explorar los datos

Abre Jupyter Notebook:

jupyter notebook

Cuando el notebook de análisis esté desarrollado, podrás utilizarlo para documentar la exploración, limpieza y visualización de los datos.

4. Abrir el dashboard

Abre Dashboard Barcelona-Betis.pbix con Power BI Desktop.

Si el informe depende de rutas locales o archivos de datos externos, tendrás que actualizar las rutas de origen para que apunten a los archivos de tu ordenador.

📈 Posibles ampliaciones

Analizar por separado pases, tiros, recuperaciones y conducciones.

Comparar los patrones espaciales de ambos equipos.

Estudiar la distribución de los tiros y los valores de goles esperados (xG), si los datos están disponibles.

Incorporar indicadores estadísticos y visualizaciones adicionales.

Mejorar la documentación del proceso de limpieza y las conclusiones del análisis.

👨‍💻 Autor

Proyecto personal de aprendizaje y desarrollo de competencias en análisis de datos, Python y Business Intelligence.

Este proyecto forma parte de mi aprendizaje práctico en análisis exploratorio de datos y visualización.

Tecnologías: Python · Pandas · Matplotlib · Jupyter Notebook · Power BI · Git