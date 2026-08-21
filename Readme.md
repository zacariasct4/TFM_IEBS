# Clasificación automática de la calidad de mediciones de irradiancia solar

Proyecto end-to-end de **Data Science, Machine Learning y Big Data** para analizar y clasificar automáticamente la calidad de mediciones solares minuto a minuto.

El sistema trabaja con datos de **GHI, DNI y DHI correspondientes a 2023 y 2024 en Sevilla**, junto con variables meteorológicas, temporales y físicas derivadas de la geometría solar. El objetivo final es predecir los códigos de calidad asociados a cada componente de irradiancia y demostrar su integración dentro de un flujo reproducible de procesamiento, almacenamiento, modelado, evaluación, interpretabilidad e inferencia.

## Objetivo

El problema se formula como una tarea de **clasificación multiclase supervisada** con tres variables objetivo:

- `codigo_ghi`
- `codigo_dni`
- `codigo_dhi`

El proyecto busca automatizar el control de calidad de las mediciones de irradiancia, reduciendo la dependencia de procedimientos manuales y combinando conocimiento físico del problema con técnicas de Machine Learning.

## Flujo general del proyecto

```text
Datos originales
      │
      ▼
Inventario y preprocesamiento
      │
      ▼
Feature engineering y EDA
      │
      ▼
Tratamiento de valores ausentes
      │
      ├───────────────┐
      ▼               ▼
 PostgreSQL        MongoDB
      │               │
      └───────┬───────┘
              ▼
      Preparación del modelado
              │
              ▼
   Comparación de modelos clásicos
              │
              ▼
      Spark + Deep Learning
              │
              ▼
 Selección y optimización final
              │
              ▼
 Interpretabilidad y análisis de error
              │
              ▼
   Simulación end-to-end
```

## Datos y variables

El dataset final contiene observaciones con frecuencia aproximada de un minuto y combina distintas familias de variables.

### Irradiancia

- `ghi`
- `dni`
- `dhi`
- `ghi_estimado`

### Geometría solar

- `elevacion_solar`
- `periodo_solar`

### Variables meteorológicas

- `temperatura`
- `velocidad_viento`
- `humedad_relativa`
- `direccion_viento_sin`
- `direccion_viento_cos`

### Variables temporales

- año
- día
- minuto
- mes codificado mediante seno/coseno
- hora codificada mediante seno/coseno

### Variables de control y calidad

- `irr_null`
- `error_balance`
- `error_balance_abs`
- `error_balance_rel`
- `var_meteo_imp`

Los datasets locales se almacenan principalmente en formato **Parquet**. Las carpetas `data/raw`, `data/interim`, `data/processed` y `data/external` se mantienen fuera del control de versiones para evitar versionar datos pesados.

## Procesamiento y preparación

El pipeline de datos incorpora:

- inventario de fuentes y variables;
- homogeneización de columnas y tipos;
- tratamiento temporal;
- cálculo de variables cíclicas;
- cálculo de variables relacionadas con la geometría solar;
- cálculo del balance entre componentes de irradiancia;
- análisis exploratorio;
- identificación de valores extremos y patrones de missing data;
- imputación controlada de variables meteorológicas;
- preparación específica de features para cada target.

## Almacenamiento

### PostgreSQL

PostgreSQL se utiliza como capa relacional para almacenar y organizar:

- mediciones procesadas;
- versiones del dataset;
- índices y vistas;
- experimentos;
- modelos y resultados asociados.

Los scripts SQL se encuentran en `sql/` e incluyen la creación de usuario/base de datos, tablas, versiones, índices, vistas y tablas de experimentación/modelos.

La configuración esperada puede definirse a partir de `.env.example`.

### MongoDB

MongoDB se utiliza para la parte documental del proyecto:

- resúmenes diarios;
- documentos de control;
- metadatos;
- referencias a visualizaciones;
- carga masiva y validación de documentos.

Las gráficas diarias se almacenan en el sistema de archivos y MongoDB conserva sus rutas y metadatos asociados.

## Machine Learning

La fase de modelado compara diferentes enfoques de clasificación y posteriormente selecciona una solución independiente para cada target.

Los modelos finales guardados en `models/final/` son:

| Target | Modelo final | Nº features |
|---|---|---:|
| `codigo_ghi` | MLP | 14 |
| `codigo_dni` | HistGradientBoostingClassifier | 18 |
| `codigo_dhi` | HistGradientBoostingClassifier | 21 |

Los artefactos finales incluyen:

- `codigo_ghi_mlp.keras`
- `codigo_ghi_scaler.joblib`
- `codigo_dni_hgb.joblib`
- `codigo_dhi_hgb.joblib`
- `model_metadata.json`

El fichero `model_metadata.json` documenta para cada target el algoritmo, conjunto de features, hiperparámetros y métricas de referencia.

## Métricas de los modelos finales

La selección no se basa únicamente en accuracy. Dado el carácter multiclase y el desequilibrio entre clases, se priorizan especialmente:

- F1 macro;
- balanced accuracy;
- F1 weighted;
- métricas por clase;
- matrices de confusión.

Métricas de referencia almacenadas para la evaluación 2023:

| Target | F1 macro | Balanced accuracy | F1 weighted |
|---|---:|---:|---:|
| `codigo_ghi` | 0.808 | 0.772 | 0.924 |
| `codigo_dni` | 0.645 | 0.635 | 0.985 |
| `codigo_dhi` | 0.516 | 0.531 | 0.903 |

Estas diferencias entre F1 macro y F1 weighted reflejan el fuerte desequilibrio de algunas clases y justifican el uso de métricas balanceadas durante la evaluación.

## Spark y Deep Learning

El proyecto incluye un bloque específico de procesamiento distribuido y Deep Learning en `14_spark_deep_learning.ipynb`.

Su objetivo es estudiar la integración de:

- Apache Spark;
- PySpark;
- Spark DataFrames;
- procesamiento distribuido;
- preparación de datos a gran escala;
- redes neuronales mediante TensorFlow/Keras.

Spark se incorpora como demostración de escalabilidad del pipeline y no como sustitución artificial del flujo principal cuando el volumen de datos no lo requiere.

## Interpretabilidad y análisis de error

El notebook `16_interpretability_and_error_analysis.ipynb` estudia el comportamiento de los modelos finales y sus errores.

Esta fase busca:

- identificar qué variables influyen más en las predicciones;
- comprobar la coherencia física de las decisiones del modelo;
- analizar los errores por target y clase;
- detectar limitaciones antes de plantear un posible despliegue.

## Solución end-to-end

El notebook final, `17_end_to_end_inference_and_solution.ipynb`, integra los componentes principales del proyecto dentro de una simulación retrospectiva de producción.

Se adopta **diciembre de 2024** como periodo de pseudo-producción:

- 1.008.000 registros anteriores se utilizan como histórico para el reentrenamiento final;
- 44.640 observaciones de diciembre de 2024 se reservan para simular inferencia posterior.

El flujo reproducido es:

```text
Datos históricos
      │
      ▼
Preparación
      │
      ▼
Reentrenamiento final
      │
      ▼
Inferencia sobre diciembre 2024
      │
      ▼
Evaluación temporal
      │
      ▼
Monitorización diaria y mensual
      │
      ▼
Persistencia de resultados
```

Esta simulación no debe interpretarse como un test totalmente independiente del proceso experimental global, sino como una demostración retrospectiva del funcionamiento esperado de la solución en producción.

Los resultados generados se guardan en `outputs/end_to_end/`:

- `predictions_december_2024.parquet`
- `daily_metrics.csv`
- `monthly_metrics.csv`
- `metrics_comparison.csv`

Métricas de la simulación de pseudo-producción:

| Target | F1 macro | Balanced accuracy |
|---|---:|---:|
| `codigo_ghi` | 0.641 | 0.608 |
| `codigo_dni` | 0.586 | 0.552 |
| `codigo_dhi` | 0.444 | 0.654 |

La simulación confirma que los modelos seleccionados pueden integrarse en un único flujo reproducible de preparación, reentrenamiento, inferencia, monitorización y persistencia.

## Estructura del repositorio

```text
TFM_IEBS/
│
├── docs/
├── models/
│   └── final/
├── notebooks/
├── outputs/
│   ├── daily_plots/
│   ├── end_to_end/
│   ├── mongodb_logs/
│   └── tables/
├── reports/
├── sql/
├── src/
│   ├── database/
│   ├── evaluation/
│   ├── models/
│   ├── mongodb/
│   └── preprocessing/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── Readme.md
```

## Notebooks

El proyecto se desarrolla de forma incremental a través de 17 notebooks:

| Nº | Notebook | Contenido |
|---:|---|---|
| 01 | `01_data_inventory.ipynb` | Inventario inicial de datos |
| 02 | `02_column_preprocessing.ipynb` | Preprocesamiento y homogeneización de columnas |
| 03 | `03_initial_eda.ipynb` | Análisis exploratorio inicial |
| 04 | `04_imputacion_de_nulos.ipynb` | Análisis e imputación de valores ausentes |
| 05 | `05_postgresql_preparation.ipynb` | Preparación y persistencia en PostgreSQL |
| 06 | `06_mongodb_connection.ipynb` | Conexión a MongoDB |
| 07 | `07_mongodb_daily_summary.ipynb` | Diseño de resúmenes diarios |
| 08 | `08_mongodb_daily_plots.ipynb` | Generación de visualizaciones diarias |
| 09 | `09_mongodb_document_insertion.ipynb` | Inserción de documentos |
| 10 | `10_mongodb_bulk_load.ipynb` | Carga masiva en MongoDB |
| 11 | `11_mongodb_validation.ipynb` | Validación de la carga documental |
| 12 | `12_model_preparation.ipynb` | Preparación del problema de modelado |
| 13 | `13_classical_model_comparison.ipynb` | Comparación de modelos clásicos |
| 14 | `14_spark_deep_learning.ipynb` | Spark y Deep Learning |
| 15 | `15_model_selection_optimization.ipynb` | Selección y optimización de modelos finales |
| 16 | `16_interpretability_and_error_analysis.ipynb` | Interpretabilidad y análisis de errores |
| 17 | `17_end_to_end_inference_and_solution.ipynb` | Solución end-to-end y pseudo-producción |

## Código reutilizable

La lógica reutilizable se separa de los notebooks dentro de `src/`:

### `src/preprocessing/`

- feature engineering;
- preparación de variables;
- transformación de tipos para modelado.

### `src/database/`

- conexiones PostgreSQL;
- carga de mediciones;
- persistencia;
- validación de base de datos.

### `src/mongodb/`

- conexión;
- construcción de documentos diarios;
- generación de gráficas;
- persistencia y carga masiva.

### `src/models/`

- construcción y entrenamiento de la MLP.

### `src/evaluation/`

- funciones comunes para evaluar predicciones y calcular métricas.

## Tecnologías principales

- Python 3.11+
- Pandas
- NumPy
- Scikit-learn
- TensorFlow / Keras
- SHAP
- Matplotlib
- PostgreSQL
- SQLAlchemy
- Psycopg
- MongoDB / PyMongo
- Apache Spark / PySpark
- pvlib
- Parquet / PyArrow / Fastparquet
- Jupyter Notebook
- Git / GitHub

## Instalación

Se recomienda utilizar un entorno virtual de Python 3.11 o superior.

```bash
python -m venv .venv
```

Activación en Windows:

```bash
.venv\Scripts\activate
```

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

El proyecto también está configurado como paquete editable mediante `pyproject.toml` y `requirements.txt` incluye `-e .`, por lo que los módulos de `src` pueden importarse directamente desde los notebooks.

## Variables de entorno

Copiar `.env.example` como `.env` y completar las credenciales locales:

```bash
cp .env.example .env
```

Variables utilizadas:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_SCHEMA
MONGODB_URI
MONGODB_DATABASE
```

El archivo `.env` está excluido del repositorio para evitar versionar credenciales.

## Reproducibilidad

El flujo lógico de ejecución es:

```text
01–04  → preparación, EDA e imputación
05     → PostgreSQL
06–11  → MongoDB
12     → preparación del modelado
13     → comparación de modelos clásicos
14     → Spark y Deep Learning
15     → selección y optimización final
16     → interpretabilidad y análisis de errores
17     → simulación end-to-end
```

Para una reproducción completa es necesario disponer localmente de los datasets que no se versionan en Git, así como de las conexiones PostgreSQL y MongoDB cuando se ejecuten los bloques correspondientes.

## Aplicabilidad

La solución puede servir como base para un sistema automático de **control de calidad de estaciones de medida de radiación solar**.

En un escenario operacional, el sistema podría:

1. recibir nuevas mediciones;
2. validar el esquema de entrada;
3. aplicar el preprocesamiento y feature engineering;
4. generar los códigos de calidad para GHI, DNI y DHI;
5. almacenar las predicciones;
6. monitorizar métricas y detectar degradaciones;
7. generar indicadores para supervisión técnica.

La aportación principal del proyecto no es únicamente la comparación de modelos, sino la construcción de un pipeline completo y reproducible que conecta **ingeniería de datos, almacenamiento relacional y documental, Machine Learning, Big Data, interpretabilidad y simulación de inferencia**.

## Contexto académico

Proyecto desarrollado como Global Project del **Máster en Data Science y Big Data de IEBS**.

## Estado

**Proyecto finalizado.**

El repositorio contiene el pipeline completo desde la preparación de los datos hasta la simulación end-to-end con los modelos finales.