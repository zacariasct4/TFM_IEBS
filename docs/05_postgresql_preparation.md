# 05. Preparación del dataset para PostgreSQL

## Objetivo

Este notebook revisa la estructura del dataset procesado `dataset_solar_2023_2024_v3.parquet` antes de su carga en PostgreSQL y genera un diccionario de datos con la información necesaria para documentar la tabla principal del proyecto.

La creación de la base de datos, las tablas, los índices y las vistas se mantiene separada en los scripts de la carpeta `sql/`.

## Dataset utilizado

- **Archivo de entrada:** `data/processed/dataset_solar_2023_2024_v3.parquet`
- **Número de filas:** 1.052.640
- **Número de columnas:** 27
- **Periodo:** 2023-2024
- **Frecuencia temporal:** un minuto

## Proceso realizado

### 1. Carga y revisión general

Se carga el dataset procesado y se comprueban sus dimensiones y primeras observaciones para verificar que el archivo puede leerse correctamente y conserva la estructura esperada.

### 2. Análisis estructural

Para cada variable se obtienen:

- tipo de dato en Pandas;
- número y porcentaje de valores nulos;
- cantidad de valores únicos.

Esta revisión permite anticipar la correspondencia entre los tipos de datos del Parquet y los tipos definidos posteriormente en PostgreSQL.

### 3. Resumen de variables numéricas

Se calculan estadísticas descriptivas de las variables numéricas, incluyendo recuento, media, desviación estándar, valores mínimos, máximos y cuartiles.

El objetivo de esta revisión no es repetir el análisis exploratorio, sino detectar posibles incompatibilidades o valores fuera de los rangos previstos antes de almacenar el dataset en la base de datos.

### 4. Revisión de variables categóricas

Se inspeccionan las frecuencias de las variables:

- `irr_null`;
- `periodo_solar`;
- `var_meteo_imp`.

Los resultados permiten confirmar los valores existentes y definir posteriormente las restricciones de calidad correspondientes en PostgreSQL.

### 5. Creación del diccionario de datos

Se documentan las 27 variables del dataset mediante los siguientes campos:

- nombre de la columna;
- descripción;
- unidad;
- tipo de dato en Pandas;
- tipo de dato propuesto en PostgreSQL;
- número y porcentaje de nulos;
- cardinalidad;
- admisión de valores nulos;
- posible participación en la clave primaria;
- regla principal de calidad.

La variable `fecha` actúa como identificador temporal único dentro de cada versión del dataset. En PostgreSQL forma parte de la clave primaria compuesta junto con `dataset_version_id`.

### 6. Exportación

El diccionario generado se exporta como:

```text
docs/data_dictionary_v3.csv
```

Se utiliza codificación `utf-8-sig` para facilitar su apertura y lectura en herramientas como Microsoft Excel.

## Resultado

El notebook genera una documentación estructurada de las 27 columnas del dataset procesado y mantiene la correspondencia entre:

```text
Dataset Parquet
→ diccionario de datos
→ tabla solar.measurements
```

El archivo resultante sirve como referencia para interpretar la estructura de la base de datos, justificar los tipos de datos elegidos y mantener la trazabilidad entre la fase de preparación y la persistencia en PostgreSQL.

## Archivos relacionados

```text
data/processed/dataset_solar_2023_2024_v3.parquet
docs/data_dictionary_v3.csv
sql/01_create_tables.sql
sql/02_insert_dataset_versions.sql
sql/03_create_indexes.sql
sql/04_create_views.sql
sql/05_create_experiment_tables.sql
src/database/connection.py
src/database/load_measurements.py
src/database/validate_database.py
```
