⚽ Análisis Exploratorio de Datos (EDA) — Real Betis vs FC Barcelona

Proyecto de análisis exploratorio de datos de un partido de fútbol mediante Python, Pandas, Matplotlib y Power BI. El objetivo es explorar la distribución espacial de los eventos del partido y crear visualizaciones que permitan identificar patrones de actividad en el terreno de juego.

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

El dashboard incorpora segmentadores para explorar los datos por equipo y jugador. También permite filtrar por tipo de acción cuando el campo correspondiente está disponible en el visual.

El mapa de calor representa la frecuencia de eventos por zona, no la calidad ni la peligrosidad de las acciones.

🗂️ Estructura del proyecto

Datos futbol/
├── data/
│   ├── raw/
│   │   └── 3773631.json
│   └── processed/
│       ├── eventos_partido.csv
│       └── tiros_partido.csv
├── src/
│   └── prepare_match.py
├── reports/
├── analisis.ipynb
├── Dashboard Barcelona-Betis.pbix
├── CampoFutbol_fondo_cesped_web-futbol.jpg
├── guia_proceso_analisis_futbol_python_powerbi.pdf
├── .gitignore
└── README.md

🚀 Cómo utilizar el proyecto

1. Clonar el repositorio

git clone https://github.com/betiman88/eda-futbol-betis-barcelona.git
cd eda-futbol-betis-barcelona

2. Preparar el entorno de Python

Es recomendable utilizar un entorno virtual:

python -m venv venv

En Windows, activa el entorno desde PowerShell:

.\venv\Scripts\Activate.ps1

Instala las librerías necesarias:

python -m pip install pandas numpy matplotlib jupyter

3. Preparar y explorar los datos

El script src/prepare_match.py se utiliza para preparar los datos del partido.

Para abrir Jupyter Notebook, ejecuta:

jupyter notebook

Después, abre analisis.ipynb para trabajar con el análisis exploratorio de datos.

4. Abrir el dashboard de Power BI

Abre Dashboard Barcelona-Betis.pbix con Power BI Desktop.

Si el informe utiliza rutas locales o archivos externos, actualiza las rutas de origen para que apunten a la ubicación de los datos en tu ordenador.

📈 Posibles ampliaciones

Analizar por separado pases, tiros, recuperaciones y conducciones.

Comparar los patrones espaciales de ambos equipos.

Estudiar la distribución de los tiros y los valores de goles esperados (xG), si están disponibles.

Incorporar indicadores estadísticos y visualizaciones adicionales.

Documentar las decisiones de limpieza y las conclusiones del análisis.

Mejorar el dashboard con nuevas visualizaciones y métricas.

👨‍💻 Autor

Proyecto personal de aprendizaje y desarrollo de competencias en análisis de datos, Python y Business Intelligence.

Este trabajo forma parte de mi aprendizaje práctico en análisis exploratorio de datos y visualización.

Tecnologías: Python · Pandas · NumPy · Matplotlib · Jupyter Notebook · Power BI · Git · GitHub
