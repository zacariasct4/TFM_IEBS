# Arquitectura final del proyecto

## 1. Propósito

La arquitectura final integra en un único flujo reproducible las etapas de **ingesta, preparación, almacenamiento, modelado, evaluación, interpretabilidad e inferencia** necesarias para clasificar automáticamente la calidad de las mediciones de irradiancia solar minuto a minuto.

El proyecto trabaja con datos de **GHI, DNI y DHI de 2023 y 2024 en Sevilla**, enriquecidos con variables temporales, meteorológicas y físicas. El dataset procesado final contiene **1.052.640 registros y 27 variables**.

La arquitectura se diseñó con una separación explícita de responsabilidades:

- **Parquet** para los datasets analíticos locales;
- **PostgreSQL** para información estructurada, trazabilidad y resultados de experimentos;
- **MongoDB** para resúmenes diarios y metadatos documentales;
- **Python / scikit-learn / TensorFlow** para procesamiento y modelado;
- **Spark / PySpark** para demostrar el procesamiento distribuido del dataset;
- **artefactos versionados de modelos** para reutilizar las configuraciones finales;
- **outputs de pseudo-producción** para monitorizar el funcionamiento end-to-end.

---

## 2. Flujo global

```text
Archivos originales 2023/2024
          │
          ▼
┌──────────────────────────────┐
│ Ingesta y preparación Python │
│ notebooks 01-04              │
└──────────────┬───────────────┘
               │
               ▼
 dataset_solar_2023_2024_v3.parquet
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ PostgreSQL  │   │   Parquet   │
│ estructurado│   │  analítico  │
└──────┬──────┘   └──────┬──────┘
       │                 │
       │                 ├───────────────┐
       ▼                 ▼               ▼
┌─────────────┐   ┌─────────────┐  ┌─────────────┐
│   MongoDB   │   │ ML clásico  │  │ Spark + DL  │
│ resúmenes   │   │ notebook 13 │  │ notebook 14 │
│ diarios     │   └──────┬──────┘  └──────┬──────┘
└─────────────┘          │                │
                        └───────┬────────┘
                                ▼
                    ┌──────────────────────┐
                    │ Selección y          │
                    │ optimización final   │
                    │ notebook 15          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Modelos finales      │
                    │ models/final/        │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    ▼                      ▼
          ┌──────────────────┐   ┌──────────────────┐
          │ Interpretabilidad│   │ End-to-End       │
          │ y análisis error │   │ pseudo-producción│
          │ notebook 16      │   │ notebook 17      │
          └──────────────────┘   └─────────┬────────┘
                                           │
                                           ▼
                                  outputs/end_to_end/
```

---

## 3. Capa de datos

### 3.1. Datos originales

El punto de partida son los datos históricos de irradiancia correspondientes a 2023 y 2024. Durante las primeras fases se analizan las fuentes, se homogeneizan columnas y fechas, se incorporan variables auxiliares y se estudia la calidad del dato.

Los datos pesados no se versionan en Git. Las carpetas locales utilizadas son:

```text
data/raw/
data/interim/
data/processed/
data/external/
```

El `.gitignore` mantiene estas carpetas fuera del control de versiones, conservando únicamente su estructura.

### 3.2. Dataset procesado

El dataset principal de modelado es:

```text
data/processed/dataset_solar_2023_2024_v3.parquet
```

Contiene **1.052.640 observaciones minuto a minuto y 27 variables**.

Incluye:

- irradiancias `ghi`, `dni`, `dhi` y `ghi_estimado`;
- variables temporales y codificaciones cíclicas;
- elevación y periodo solar;
- temperatura, humedad y viento;
- errores de balance físico;
- indicadores de imputación y nulos;
- códigos de calidad `codigo_ghi`, `codigo_dni` y `codigo_dhi`.

Parquet se mantiene como formato analítico principal por su eficiencia de lectura, tipado y compatibilidad con Pandas y Spark.

---

## 4. Capa relacional: PostgreSQL

PostgreSQL actúa como repositorio estructurado y trazable del proyecto.

Configuración principal:

```text
Base de datos: solar_irradiance_db
Esquema: solar
```

### 4.1. Datos y versionado

Las tablas base son:

- `solar.dataset_versions`: registra las distintas versiones de los datasets y su estado de procesamiento;
- `solar.measurements`: almacena las mediciones procesadas minuto a minuto asociadas a una versión de dataset.

Se incorporan restricciones de integridad sobre fechas, rangos físicos, variables cíclicas, periodo solar y dominios de los códigos de calidad.

### 4.2. Modelos y resultados

Para la fase de modelado se utilizan las tablas:

- `solar.models`;
- `solar.results`.

En ellas se almacenan, por modelo:

- versión del dataset;
- algoritmo;
- target;
- años de entrenamiento y test;
- número y listado de features;
- hiperparámetros;
- F1 macro;
- balanced accuracy;
- F1 weighted.

El repositorio contiene además las tablas `solar.model_experiments` y `solar.model_metrics`, preparadas para un registro más general de experimentos y métricas.

### 4.3. Índices y vistas

Los scripts de `sql/` crean los índices y vistas necesarios para facilitar consultas y mantener separada la lógica de persistencia de los notebooks.

---

## 5. Capa documental: MongoDB

MongoDB dejó de ser un componente opcional y forma parte de la arquitectura final.

Su función es representar cada día como un documento agregado, evitando duplicar el almacenamiento minuto a minuto que ya se resuelve en PostgreSQL.

La colección principal es:

```text
daily_summaries
```

Cada documento incorpora, entre otros elementos:

- identificación de fecha y versión del dataset;
- cobertura diaria;
- estadísticas de irradiancia;
- estadísticas meteorológicas;
- variables físicas;
- distribución de códigos de calidad;
- indicadores de procesamiento;
- rutas y metadatos de las gráficas diarias.

La carga masiva procesa las **731 fechas** comprendidas entre el 1 de enero de 2023 y el 31 de diciembre de 2024. El resultado final de la carga fue:

- 731 fechas disponibles;
- 731 documentos procesados correctamente;
- 0 fechas con error.

Las dos visualizaciones generadas por día se almacenan en el sistema de archivos y MongoDB conserva sus referencias, evitando almacenar binarios innecesariamente dentro de la base documental.

---

## 6. Capa de código reutilizable

La lógica reutilizable se concentra en `src/` para evitar duplicarla dentro de los notebooks.

```text
src/
├── database/
├── evaluation/
├── models/
├── mongodb/
└── preprocessing/
```

### `src/database/`

Responsable de:

- conexión con PostgreSQL;
- carga de mediciones;
- consulta de fechas disponibles;
- persistencia;
- validación de base de datos.

### `src/mongodb/`

Responsable de:

- conexión con MongoDB;
- construcción de documentos diarios;
- generación de gráficas;
- procesamiento diario;
- carga y persistencia documental.

### `src/preprocessing/`

Responsable de:

- feature engineering;
- conversión de tipos;
- preparación de variables para los modelos.

### `src/models/`

Contiene la lógica reutilizable asociada a las redes neuronales MLP.

### `src/evaluation/`

Centraliza el cálculo de métricas y la evaluación de predicciones.

---

## 7. Procesamiento distribuido y Deep Learning

El notebook `14_spark_deep_learning.ipynb` incorpora **Apache Spark / PySpark** para:

- cargar el dataset Parquet mediante Spark DataFrames;
- validar el esquema;
- realizar transformaciones;
- separar temporalmente los datos;
- analizar distribuciones;
- preparar la información antes del modelado.

Posteriormente se utiliza **TensorFlow/Keras** para entrenar redes MLP.

Spark no sustituye al procesamiento con Pandas en todas las etapas. Su incorporación demuestra cómo la capa analítica puede trasladarse a un entorno distribuido cuando el volumen de datos o el escenario operativo lo justifiquen.

---

## 8. Capa de Machine Learning

El problema se divide en tres tareas de clasificación supervisada:

```text
codigo_ghi
codigo_dni
codigo_dhi
```

La comparación de modelos se realiza en los notebooks 13 y 14 y la selección/optimización definitiva en el notebook 15.

Los modelos finales son:

| Target | Modelo final | Features |
|---|---|---:|
| `codigo_ghi` | MLP | 14 |
| `codigo_dni` | HistGradientBoostingClassifier | 18 |
| `codigo_dhi` | HistGradientBoostingClassifier | 21 |

Los artefactos se almacenan en:

```text
models/final/
```

con los siguientes archivos:

```text
codigo_ghi_mlp.keras
codigo_ghi_scaler.joblib
codigo_dni_hgb.joblib
codigo_dhi_hgb.joblib
model_metadata.json
```

`model_metadata.json` funciona como contrato de reconstrucción de los modelos: conserva features, hiperparámetros, algoritmo y métricas de referencia.

---

## 9. Evaluación e interpretabilidad

La evaluación prioriza métricas robustas frente al fuerte desequilibrio de clases:

- F1 macro como métrica principal;
- balanced accuracy;
- F1 weighted;
- métricas por clase;
- matrices de confusión.

El notebook 16 añade una capa específica de interpretabilidad y análisis de errores mediante técnicas como:

- Permutation Importance;
- SHAP;
- análisis de errores por condiciones solares, temporales y de calidad del dato.

Esta capa permite comprobar no solo cuánto aciertan los modelos, sino también qué variables sostienen sus decisiones y dónde se concentran sus limitaciones.

---

## 10. Capa end-to-end y pseudo-producción

El notebook `17_end_to_end_inference_and_solution.ipynb` integra la arquitectura en una simulación retrospectiva de funcionamiento en producción.

Se define:

- histórico hasta el 30 de noviembre de 2024: **1.008.000 registros**;
- pseudo-producción en diciembre de 2024: **44.640 registros**.

Las configuraciones finales quedan congeladas y los modelos se reentrenan únicamente con la información disponible antes de diciembre.

El flujo final es:

```text
histórico
   ↓
preparación
   ↓
reentrenamiento final
   ↓
inferencia
   ↓
evaluación temporal
   ↓
monitorización diaria/mensual
   ↓
persistencia de resultados
```

Los artefactos generados se guardan en:

```text
outputs/end_to_end/
```

con:

```text
predictions_december_2024.parquet
daily_metrics.csv
monthly_metrics.csv
metrics_comparison.csv
```

Esta fase demuestra la integración técnica de la solución, pero no debe interpretarse como un despliegue real ni como un test completamente independiente del proceso experimental global.

---

## 11. Configuración y reproducibilidad

El proyecto requiere **Python 3.11 o superior** y sus dependencias están definidas en:

```text
requirements.txt
pyproject.toml
```

Las credenciales se mantienen fuera del repositorio mediante `.env`.

`.env.example` documenta las variables necesarias para:

- PostgreSQL;
- MongoDB Atlas.

El proyecto está configurado como paquete editable, permitiendo importar directamente la lógica de `src` desde los notebooks.

---

## 12. Decisiones arquitectónicas principales

### PostgreSQL y MongoDB cumplen funciones distintas

PostgreSQL conserva el dato estructurado y trazable; MongoDB almacena agregados diarios y metadatos documentales. No se utilizan dos bases de datos para resolver el mismo problema.

### Parquet se mantiene como formato analítico

Evita depender de la base de datos para cada experimento y facilita el trabajo tanto con Pandas como con Spark.

### Los notebooks orquestan; `src` reutiliza

La lógica que debe repetirse se extrae a módulos Python. Los notebooks quedan orientados a experimentación, explicación y ejecución.

### Los modelos finales se acompañan de metadatos

No basta con guardar los binarios. `model_metadata.json` permite conocer exactamente con qué variables e hiperparámetros debe reconstruirse cada solución.

### La pseudo-producción se mantiene separada de la selección

Diciembre de 2024 se utiliza para demostrar inferencia y monitorización, no para volver a seleccionar features o hiperparámetros.

---

## 13. Arquitectura final resumida

La solución final conecta de forma coherente:

**datos solares → ETL y feature engineering → Parquet/PostgreSQL → MongoDB → modelado clásico y Deep Learning → selección final → interpretabilidad → pseudo-producción y monitorización**.

La arquitectura resultante no pretende reproducir una plataforma de producción empresarial completa, sino demostrar una solución académica end-to-end, reproducible y escalable conceptualmente para el control automático de calidad de mediciones solares.