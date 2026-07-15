# Documentación del notebook `02_column_preprocessing.ipynb`

## 1. Propósito

Este notebook estandariza los nombres y esquemas de los datos de 2023 y 2024, prepara la elevación solar necesaria para el análisis y genera un dataset integrado para las siguientes fases del proyecto.

Es el primer paso de transformación de datos. Los ficheros originales permanecen en `data/raw`, mientras que las versiones estandarizadas se almacenan en `data/interim` y el dataset integrado se almacena en `data/processed`.

## 2. Alcance

El notebook realiza las siguientes tareas:

- carga de los datasets brutos;
- normalización de nombres de columnas;
- incorporación de la columna de año en 2024;
- exportación de datos estandarizados a Parquet;
- estandarización de la elevación solar de 2023;
- generación de la elevación solar de 2024 mediante `pvlib`;
- truncamiento de elevaciones solares negativas a cero;
- comprobación básica de duplicados y orden temporal;
- integración de irradiancias y elevación solar;
- concatenación de 2023 y 2024;
- exportación del dataset conjunto.

## 3. Entradas

El código actual espera los siguientes ficheros:

```text
data/raw/datos_2023.xlsx
data/raw/datos_2024.xlsx
data/raw/alturas_2023.xlsx
```

Debe mantenerse coherencia entre estos nombres y los empleados en el notebook de inventario. En la ejecución anterior, el archivo de elevaciones aparecía como `altura_min_sevilla.xlsx`; por tanto, conviene adoptar un único nombre en todo el proyecto.

## 4. Dependencias

```python
pandas
pathlib
pvlib
matplotlib
pyarrow
```

`pyarrow` es necesario para guardar archivos Parquet con `pandas`.

Instalación orientativa:

```bash
pip install pandas pvlib matplotlib pyarrow openpyxl
```

## 5. Convención de nombres

Se aplica una convención homogénea:

- minúsculas;
- formato `snake_case`;
- ausencia de espacios;
- ausencia de símbolos de unidades en el nombre;
- nombres consistentes entre años.

Mapeo principal:

| Nombre original | Nombre estandarizado |
|---|---|
| `Ano` | `ano` |
| `Mes` | `mes` |
| `Dia` | `dia` |
| `Hora` | `hora` |
| `Minuto` | `minuto` |
| `Fecha` | `fecha` |
| `GHI` | `ghi` |
| `DNI` | `dni` |
| `DHI` | `dhi` |
| `Temperatura [°C]` | `temperatura` |
| `Velocidad del viento [m/s]` | `velocidad_viento` |
| `Direccion del viento [º]` | `direccion_viento` |
| `Humedad Relativa [%]` | `humedad_relativa` |
| `Codigo GHI` | `codigo_ghi` |
| `Codigo DNI` | `codigo_dni` |
| `Codigo dHI` | `codigo_dhi` |
| `altura` | `elevacion_solar` |
| `Min` | `minuto` |
| `Año` | `ano` |

Las unidades deben conservarse en el diccionario de datos y en la documentación, aunque no formen parte del nombre de la columna.

## 6. Flujo de trabajo

### 6.1. Carga de datos

Se cargan los tres ficheros Excel mediante `pandas.read_excel()`:

```python
df_2023 = pd.read_excel("../data/raw/datos_2023.xlsx")
df_2024 = pd.read_excel("../data/raw/datos_2024.xlsx")
df_alturas_2023 = pd.read_excel("../data/raw/alturas_2023.xlsx")
```

### 6.2. Estandarización de los datos de 2023

Se renombran las columnas conforme al diccionario definido. No se modifican todavía:

- valores ausentes;
- posibles valores de error;
- códigos de calidad;
- unidades;
- tipos numéricos.

El objetivo de esta fase es homogeneizar el esquema, no limpiar definitivamente los valores.

### 6.3. Estandarización de los datos de 2024

Se aplica el mismo mapeo y se inserta la columna:

```python
df_2024.insert(0, "ano", 2024)
```

Con ello, ambos años comparten el mismo conjunto y orden general de variables.

### 6.4. Almacenamiento intermedio

Los datos estandarizados se guardan en formato Parquet:

```text
data/interim/datos_2023_standardized.parquet
data/interim/datos_2024_standardized.parquet
```# Documentación del notebook `02_column_preprocessing.ipynb`

## 1. Propósito

Este notebook transforma los datos brutos de irradiancia solar de 2023 y 2024 para generar un esquema homogéneo y apto para las fases posteriores del proyecto.

El procesamiento incluye:

- normalización de los nombres de las columnas;
- incorporación de la columna de año en el dataset de 2024;
- codificación cíclica de variables periódicas;
- conversión de los datasets intermedios a formato Parquet;
- limpieza del fichero original de elevación solar de 2023;
- validación de `pvlib` frente a las elevaciones observadas en 2023;
- recuperación de elevaciones solares negativas durante la noche;
- generación de la elevación solar de 2024;
- integración de las mediciones con la elevación solar;
- concatenación de los datos de 2023 y 2024.

El resultado principal es un dataset conjunto de 1.052.640 registros, preparado para el análisis exploratorio, la ingeniería de características y el modelado.

---

## 2. Entradas

El notebook utiliza los siguientes archivos:

```text
data/raw/datos_2023.xlsx
data/raw/datos_2024.xlsx
data/raw/alturas_2023.xlsx
```

### `datos_2023.xlsx`

Contiene 525.600 observaciones, correspondientes a todos los minutos de 2023.

### `datos_2024.xlsx`

Contiene 527.040 observaciones, correspondientes a todos los minutos del año bisiesto 2024.

El archivo no incluye originalmente una columna de año, por lo que se añade durante el preprocesamiento.

### `alturas_2023.xlsx`

Contiene inicialmente 525.601 registros de elevación solar. El último registro corresponde al primer minuto de 2024 y se elimina para obtener exactamente las 525.600 observaciones de 2023.

---

## 3. Dependencias

El notebook utiliza las siguientes librerías:

```python
pandas
numpy
pathlib
pvlib
matplotlib
```

Para la escritura en formato Parquet se necesita también un motor compatible, normalmente:

```bash
pip install pyarrow
```

Para la lectura de archivos Excel:

```bash
pip install openpyxl
```

---

## 4. Normalización de columnas

Se aplica un diccionario común de nombres para los datasets de 2023 y 2024.

| Nombre original | Nombre estandarizado |
|---|---|
| `Ano` | `ano` |
| `Mes` | `mes` |
| `Dia` | `dia` |
| `Hora` | `hora` |
| `Minuto` | `minuto` |
| `Fecha` | `fecha` |
| `GHI` | `ghi` |
| `DNI` | `dni` |
| `DHI` | `dhi` |
| `Temperatura [°C]` | `temperatura` |
| `Velocidad del viento [m/s]` | `velocidad_viento` |
| `Direccion del viento [º]` | `direccion_viento` |
| `Humedad Relativa [%]` | `humedad_relativa` |
| `Codigo GHI` | `codigo_ghi` |
| `Codigo DNI` | `codigo_dni` |
| `Codigo dHI` | `codigo_dhi` |

En el dataset de 2024 se añade:

```python
df_2024.insert(0, "ano", 2024)
```

Después de esta operación, ambos datasets tienen inicialmente 16 columnas y el mismo esquema básico.

---

## 5. Codificación cíclica

Las variables `direccion_viento`, `hora` y `mes` tienen naturaleza periódica. Por ejemplo:

- 23:00 y 00:00 son horas próximas;
- diciembre y enero son meses consecutivos;
- 359° y 0° representan direcciones casi idénticas.

Una representación numérica directa no conserva correctamente esta proximidad. Por ello se crean pares de variables seno y coseno.

### Dirección del viento

```python
direccion_viento_sin = sin(direccion_viento)
direccion_viento_cos = cos(direccion_viento)
```

En el código se convierte primero la dirección de grados a radianes:

```python
np.sin(np.radians(df["direccion_viento"]))
np.cos(np.radians(df["direccion_viento"]))
```

### Hora del día

```python
hora_sin = sin(2π · hora / 24)
hora_cos = cos(2π · hora / 24)
```

### Mes del año

```python
mes_sin = sin(2π · (mes - 1) / 12)
mes_cos = cos(2π · (mes - 1) / 12)
```

Después de generar las nuevas variables se eliminan las columnas originales:

```text
direccion_viento
hora
mes
```

Esta transformación evita discontinuidades artificiales y facilita el aprendizaje de patrones temporales y meteorológicos por parte de los modelos.

---

## 6. Archivos intermedios de mediciones

Los datasets estandarizados se guardan en:

```text
data/interim/datos_2023_standardized.parquet
data/interim/datos_2024_standardized.parquet
```

El uso de Parquet permite:

- reducir el tamaño de almacenamiento;
- conservar los tipos de datos;
- acelerar las operaciones de lectura y escritura;
- facilitar la integración con pandas, Spark y motores SQL.

---

## 7. Preparación de la elevación solar de 2023

El fichero original de elevaciones contiene 525.601 registros. El último corresponde a:

```text
2024-01-01 00:00:00
```

Este registro se elimina:

```python
df_alturas_2023.drop(
    axis=0,
    index=len(df_alturas_2023) - 1,
    inplace=True
)
```

Tras la eliminación, el dataset contiene 525.600 observaciones, una por cada minuto de 2023.

Las columnas se renombran mediante la ampliación del diccionario anterior:

| Nombre original | Nombre estandarizado |
|---|---|
| `Año` | `ano` |
| `Min` | `minuto` |
| `altura` | `elevacion_solar` |

La columna `elevacion_solar` representa un ángulo medido en grados, no una altura expresada en unidades de longitud.

---

## 8. Validación de `pvlib` con los datos de 2023

Antes de utilizar `pvlib` para generar los valores de 2024, el notebook reproduce las elevaciones solares de 2023 y las compara con el fichero disponible.

### Localización empleada

| Parámetro | Valor |
|---|---:|
| Latitud | 37,41° |
| Longitud | -6,01° |
| Altitud | 12 m |
| Zona horaria configurada | `Europe/Madrid` |
| Método de cálculo | `nrel_numpy` |

La estación se define mediante:

```python
station = Location(
    latitude=37.41,
    longitude=-6.01,
    tz="Europe/Madrid",
    altitude=12,
    name="Estacion_Sevilla"
)
```

### Secuencia temporal

Se generan todos los minutos de 2023 en UTC:

```python
timestamps_utc = pd.date_range(
    start="2023-01-01 00:00:00",
    end="2024-01-01 00:00:00",
    freq="1min",
    inclusive="left",
    tz="UTC"
)
```

La posición solar se calcula mediante:

```python
station.get_solarposition(
    times=timestamps_utc,
    method="nrel_numpy"
)
```

### Variable seleccionada

Se selecciona `apparent_elevation`, que representa la elevación solar aparente corregida por refracción atmosférica.

Para realizar inicialmente la comparación con el fichero original, los valores negativos calculados por `pvlib` se truncan a cero, ya que el dataset proporcionado utiliza cero durante la noche.

### Resultado de la comparación

El error se define como:

```text
error = elevación observada − elevación calculada con pvlib
```

Las métricas obtenidas son:

| Métrica | Error angular |
|---|---:|
| Media | -0,034959° |
| Desviación estándar | 0,137132° |
| Mínimo | -0,784864° |
| Mediana | 0° |
| Máximo | 0,270609° |

El error absoluto máximo es inferior a 0,8°, por lo que el notebook considera que `pvlib` reproduce con suficiente precisión los datos disponibles y puede utilizarse para generar la elevación solar de 2024.

También se representa:

- la comparación de las curvas del 1 de enero de 2023;
- el error medio diario a lo largo de 2023.

---

## 9. Recuperación de elevaciones nocturnas de 2023

El fichero original sustituye por cero las elevaciones negativas, correspondientes a periodos nocturnos.

Después de validar `pvlib`, estos ceros se reemplazan por los valores negativos calculados:

```python
df_alturas_2023["elevacion_solar"] = np.where(
    df_alturas_2023["elevacion_solar"] == 0,
    solar_position_2023["apparent_elevation"].values,
    df_alturas_2023["elevacion_solar"]
)
```

Con esta decisión se conserva información sobre la posición del Sol por debajo del horizonte.

La elevación negativa puede resultar útil para:

- diferenciar claramente día, crepúsculo y noche;
- crear variables temporales continuas;
- analizar transiciones de amanecer y atardecer;
- desarrollar modelos secuenciales o de series temporales;
- detectar irradiancias incoherentes durante la noche.

El resultado se guarda en:

```text
data/interim/elevacion_2023_standardized.parquet
```

---

## 10. Generación de la elevación solar de 2024

Se generan todos los minutos del año bisiesto 2024:

```python
timestamps_utc = pd.date_range(
    start="2024-01-01 00:00:00",
    end="2025-01-01 00:00:00",
    freq="1min",
    inclusive="left",
    tz="UTC"
)
```

Se calcula `apparent_elevation` para cada timestamp mediante `pvlib`.

A diferencia de la primera comparación de 2023, los valores negativos no se truncan. De este modo, el dataset de 2024 mantiene la misma convención final aplicada a 2023.

Se generan las siguientes columnas:

| Columna | Descripción |
|---|---|
| `fecha` | Timestamp sin información explícita de zona horaria |
| `ano` | Año |
| `mes` | Mes |
| `dia` | Día del año |
| `hora` | Hora |
| `minuto` | Minuto |
| `elevacion_solar` | Elevación solar aparente en grados |

La columna `dia` se calcula con:

```python
df_alturas_2024["fecha"].dt.dayofyear
```

Por tanto, en los datasets de elevación solar representa el día del año, con valores entre 1 y 365 o 366.

El dataset de 2024 contiene:

```text
527.040 filas
7 columnas
```

Las comprobaciones realizadas indican:

```text
Duplicados en fecha: 0
Serie temporal ordenada: True
Valores ausentes: 0
```

La salida se guarda en:

```text
data/interim/elevacion_2024_standardized.parquet
```

---

## 11. Integración de mediciones y elevación solar

Las mediciones de cada año se combinan con su correspondiente elevación solar utilizando `fecha` como clave:

```python
df_2023_integrated = df_2023.merge(
    df_alturas_2023[["fecha", "elevacion_solar"]],
    on="fecha",
    how="left",
    validate="one_to_one"
)
```

La misma operación se aplica a 2024.

El parámetro:

```python
validate="one_to_one"
```

comprueba que cada timestamp aparece una sola vez en cada dataset. Esto evita que los duplicados multipliquen silenciosamente el número de registros.

Después del `merge` se verifica que todas las filas tengan elevación solar:

```python
assert df_2023_integrated["elevacion_solar"].notna().all()
assert df_2024_integrated["elevacion_solar"].notna().all()
```

---

## 12. Esquema integrado

Después de la integración, las columnas se ordenan de la siguiente manera:

```text
ano
mes_sin
mes_cos
dia
hora_sin
hora_cos
minuto
fecha
ghi
dni
dhi
elevacion_solar
temperatura
velocidad_viento
humedad_relativa
direccion_viento_sin
direccion_viento_cos
codigo_ghi
codigo_dni
codigo_dhi
```

### Diccionario de datos

| Variable | Unidad o dominio | Función |
|---|---|---|
| `ano` | Año | Contexto temporal |
| `mes_sin` | [-1, 1] | Codificación cíclica del mes |
| `mes_cos` | [-1, 1] | Codificación cíclica del mes |
| `dia` | Día del mes en las mediciones | Contexto temporal |
| `hora_sin` | [-1, 1] | Codificación cíclica de la hora |
| `hora_cos` | [-1, 1] | Codificación cíclica de la hora |
| `minuto` | 0–59 | Contexto temporal |
| `fecha` | datetime | Clave temporal |
| `ghi` | W/m² | Irradiancia global horizontal |
| `dni` | W/m² | Irradiancia directa normal |
| `dhi` | W/m² | Irradiancia difusa horizontal |
| `elevacion_solar` | grados | Posición aparente del Sol |
| `temperatura` | °C | Variable meteorológica |
| `velocidad_viento` | m/s | Variable meteorológica |
| `humedad_relativa` | % | Variable meteorológica |
| `direccion_viento_sin` | [-1, 1] | Dirección del viento codificada |
| `direccion_viento_cos` | [-1, 1] | Dirección del viento codificada |
| `codigo_ghi` | Categoría | Etiqueta de calidad de GHI |
| `codigo_dni` | Categoría | Etiqueta de calidad de DNI |
| `codigo_dhi` | Categoría | Etiqueta de calidad de DHI |

---

## 13. Concatenación de 2023 y 2024

Los datasets integrados se concatenan:

```python
df_all = (
    pd.concat(
        [df_2023_integrated, df_2024_integrated],
        ignore_index=True
    )
    .sort_values("fecha")
    .reset_index(drop=True)
)
```

Número total esperado de observaciones:

```text
525.600 + 527.040 = 1.052.640
```

El dataset final se exporta a:

```text
data/processed/dataset_solar_2023_2024_v1.parquet
```

Este fichero constituye la entrada principal para:

- análisis exploratorio;
- estudio de los códigos de calidad;
- definición de targets;
- creación de reglas físicas;
- ingeniería de características;
- entrenamiento y evaluación de modelos;
- carga posterior en PostgreSQL o Spark.

---

## 14. Salidas del notebook

### Datos intermedios

```text
data/interim/datos_2023_standardized.parquet
data/interim/datos_2024_standardized.parquet
data/interim/elevacion_2023_standardized.parquet
data/interim/elevacion_2024_standardized.parquet
```

### Dataset procesado

```text
data/processed/dataset_solar_2023_2024_v1.parquet
```

---

## 15. Decisiones técnicas adoptadas

### Uso de Parquet

Se utiliza Parquet por su eficiencia de almacenamiento, velocidad de lectura y compatibilidad con herramientas de Data Science y Big Data.

### Uso de `apparent_elevation`

Se selecciona la elevación aparente porque incorpora el efecto de la refracción atmosférica y reproduce de forma muy próxima el fichero disponible para 2023.

### Conservación de elevaciones negativas

Los valores negativos se mantienen en el dataset final para representar la posición nocturna del Sol y conservar continuidad física y temporal.

### Codificación cíclica

La hora, el mes y la dirección del viento se transforman mediante seno y coseno para evitar discontinuidades artificiales.

### Integración uno a uno

Los merges se validan como relaciones uno a uno para impedir duplicaciones de filas.

### Dataset único para ambos años

Los datos se concatenan en una única tabla analítica para facilitar el análisis conjunto y la validación temporal entre años.

---

## 16. Incidencias y mejoras pendientes

### 16.1. Error tipográfico al ordenar columnas

Dentro de `codify_cyclic_features()` aparece:

```python
df.colums = ordered_columns
```

La propiedad correcta es:

```python
df = df[ordered_columns]
```

o bien:

```python
df = df.reindex(columns=ordered_columns)
```

La instrucción actual genera una advertencia y no cambia realmente el orden de las columnas en los Parquet intermedios.

El orden sí se corrige posteriormente en los datasets integrados, pero conviene solucionar el error para que todas las salidas tengan un esquema consistente.

### 16.2. Semántica diferente de la columna `dia`

En los datasets de mediciones, `dia` representa el día del mes.

En los datasets de elevación solar, `dia` representa el día del año.

La integración final utiliza solamente `fecha` y `elevacion_solar`, por lo que esta diferencia no afecta al `merge`. Sin embargo, puede generar confusión en la documentación o en futuras transformaciones.

Se recomienda utilizar nombres explícitos:

```text
dia_mes
dia_ano
```

### 16.3. Convención temporal

La posición solar se calcula con timestamps UTC. Después se elimina la información de zona horaria mediante:

```python
tz_convert(None)
```

o:

```python
tz_localize(None)
```

Por tanto, `fecha` queda como un timestamp sin zona horaria explícita, pero derivado de una secuencia UTC.

La buena correspondencia con las elevaciones de 2023 respalda empíricamente esta alineación. Aun así, la convención debe explicarse de forma consistente en todo el proyecto y no denominarse hora local sin una conversión explícita.

### 16.4. Creación de `data/processed`

El notebook crea la carpeta `data/interim`, pero no crea explícitamente `data/processed`.

Antes de guardar el dataset final se recomienda incluir:

```python
PROCESSED_PATH = Path("../data/processed")
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
```

### 16.5. Validaciones adicionales

Conviene añadir comprobaciones automáticas:

```python
assert len(df_2023) == 525_600
assert len(df_2024) == 527_040
assert len(df_alturas_2023) == 525_600
assert len(df_alturas_2024) == 527_040
assert len(df_all) == 1_052_640

assert df_2023["fecha"].is_unique
assert df_2024["fecha"].is_unique
assert df_alturas_2023["fecha"].is_unique
assert df_alturas_2024["fecha"].is_unique

assert df_all["fecha"].is_monotonic_increasing
```

También debe verificarse que el notebook se ejecuta completamente desde un kernel limpio.

---

## 17. Estructura de carpetas esperada

```text
project/
├── data/
│   ├── raw/
│   │   ├── datos_2023.xlsx
│   │   ├── datos_2024.xlsx
│   │   └── alturas_2023.xlsx
│   ├── interim/
│   │   ├── datos_2023_standardized.parquet
│   │   ├── datos_2024_standardized.parquet
│   │   ├── elevacion_2023_standardized.parquet
│   │   └── elevacion_2024_standardized.parquet
│   └── processed/
│       └── dataset_solar_2023_2024_v1.parquet
├── notebooks/
│   ├── 01_data_inventory.ipynb
│   └── 02_column_preprocessing.ipynb
└── docs/
    └── 02_column_preprocessing.md
```

---

## 18. Criterio de finalización

El notebook puede considerarse completado cuando:

- los nombres de las columnas son homogéneos;
- el dataset de 2024 incluye el año;
- las variables periódicas están codificadas correctamente;
- se elimina el registro adicional de elevación de 2023;
- la precisión de `pvlib` queda validada cuantitativamente;
- las elevaciones negativas se conservan de forma consistente;
- se genera la elevación solar completa de 2024;
- los merges son uno a uno;
- no existen elevaciones ausentes después de la integración;
- el dataset final contiene 1.052.640 registros;
- las carpetas de salida se crean automáticamente;
- el notebook puede ejecutarse de principio a fin desde un kernel limpio.

El uso de Parquet permite:

- menor tamaño de almacenamiento;
- lectura y escritura más rápidas;
- conservación de tipos;
- integración eficiente con pandas, Spark y motores analíticos.

### 6.5. Estandarización de la elevación solar de 2023

Se renombran las variables temporales y la columna `altura`:

```text
altura → elevacion_solar
```

La elevación solar se expresa en grados. Los valores negativos ya aparecen truncados a cero en el fichero de origen, representando periodos en los que el Sol está por debajo del horizonte.

La salida se guarda como:

```text
data/interim/elevacion_2023_standardized.parquet
```

### 6.6. Generación de la elevación solar de 2024

Se crea una localización de Sevilla mediante `pvlib.location.Location` con los siguientes parámetros:

| Parámetro | Valor |
|---|---:|
| Latitud | 37,41° |
| Longitud | -6,01° |
| Altitud | 12 m |
| Zona horaria | `Europe/Madrid` |

La posición solar se calcula con:

```python
station.get_solarposition(
    times=timestamps_utc,
    method="nrel_numpy"
)
```

Se obtienen, entre otras, dos variables:

- `elevation`: elevación geométrica;
- `apparent_elevation`: elevación aparente corregida por refracción atmosférica.

El notebook selecciona `apparent_elevation` por su mayor correspondencia conceptual con la posición visible del Sol y con el funcionamiento descrito para la estación.

Los valores negativos se reemplazan por cero:

```python
.clip(lower=0)
```

La salida final contiene:

| Columna | Descripción |
|---|---|
| `fecha` | Marca temporal por minuto |
| `ano` | Año |
| `mes` | Mes |
| `dia` | Día según la convención del fichero de elevaciones |
| `hora` | Hora |
| `minuto` | Minuto |
| `elevacion_solar` | Elevación solar aparente en grados, truncada a cero |

Se generan 527.040 registros, correspondientes a todos los minutos del año bisiesto 2024.

### 6.7. Validación temporal básica

Se comprueba:

```python
df_alturas_2024["fecha"].duplicated().sum()
df_alturas_2024["fecha"].is_monotonic_increasing
```

En la ejecución documentada:

- no se detectaron fechas duplicadas;
- la serie estaba ordenada cronológicamente.

La elevación estandarizada de 2024 se guarda en:

```text
data/interim/elevacion_2024_standardized.parquet
```

### 6.8. Integración con las mediciones

Cada dataset anual se combina con su elevación solar mediante:

```python
merge(
    ...,
    on="fecha",
    how="left",
    validate="one_to_one"
)
```

`validate="one_to_one"` exige que cada timestamp aparezca como máximo una vez en ambos datasets. Esta restricción evita integraciones silenciosamente incorrectas.

Después se comprueba que todas las observaciones hayan recibido elevación solar:

```python
assert df_integrated["elevacion_solar"].notna().all()
```

### 6.9. Concatenación de los años

Los dos datasets integrados se concatenan, ordenan por fecha y reinician su índice:

```python
df_all = (
    pd.concat(
        [df_2023_integrated, df_2024_integrated],
        ignore_index=True
    )
    .sort_values("fecha")
    .reset_index(drop=True)
)
```

La salida esperada contiene:

```text
525.600 + 527.040 = 1.052.640 registros
```

### 6.10. Dataset procesado

El resultado se exporta a:

```text
data/processed/dataset_solar_2023_2024_v1.parquet
```

Este fichero constituye la entrada principal prevista para:

- análisis exploratorio;
- definición de targets;
- reglas físicas;
- feature engineering;
- carga en PostgreSQL;
- procesamiento con Spark;
- entrenamiento de modelos.

## 7. Salidas

### Zona intermedia

```text
data/interim/datos_2023_standardized.parquet
data/interim/datos_2024_standardized.parquet
data/interim/elevacion_2023_standardized.parquet
data/interim/elevacion_2024_standardized.parquet
```

### Zona procesada

```text
data/processed/dataset_solar_2023_2024_v1.parquet
```

## 8. Diccionario de datos resultante

| Variable | Tipo esperado | Unidad | Función |
|---|---|---|---|
| `ano` | entero | — | Variable temporal |
| `mes` | entero | — | Variable temporal |
| `dia` | entero | — | Día según convención temporal |
| `hora` | entero | — | Variable temporal |
| `minuto` | entero | — | Variable temporal |
| `fecha` | datetime | — | Clave temporal |
| `ghi` | decimal | W/m² | Variable predictora y magnitud evaluada |
| `dni` | decimal | W/m² | Variable predictora y magnitud evaluada |
| `dhi` | decimal | W/m² | Variable predictora y magnitud evaluada |
| `temperatura` | decimal | °C | Variable meteorológica |
| `velocidad_viento` | decimal | m/s | Variable meteorológica |
| `direccion_viento` | decimal | grados | Variable meteorológica |
| `humedad_relativa` | decimal | % | Variable meteorológica |
| `codigo_ghi` | entero | — | Target inicial de calidad GHI |
| `codigo_dni` | entero | — | Target inicial de calidad DNI |
| `codigo_dhi` | entero | — | Target inicial de calidad DHI |
| `elevacion_solar` | decimal | grados | Variable física auxiliar |

## 9. Decisiones técnicas

### Parquet como formato de trabajo

Se emplea Parquet porque el dataset supera el millón de registros y se utilizará posteriormente con herramientas analíticas y de Big Data.

### Elevación aparente

Se utiliza `apparent_elevation` en lugar de `elevation`, ya que incorpora la refracción atmosférica y aproxima mejor la posición visible del Sol.

### Elevaciones nocturnas a cero

Los valores negativos se sustituyen por cero para mantener la misma convención del fichero de 2023 y facilitar la separación entre periodos diurnos y nocturnos.

### Integración uno a uno

La clave temporal se valida como relación uno a uno para impedir multiplicaciones de filas por duplicados.

## 10. Validaciones que deben conservarse

Antes de considerar el dataset definitivo, se recomienda incluir:

```python
assert df_2023["fecha"].is_unique
assert df_2024["fecha"].is_unique
assert df_alturas_2023["fecha"].is_unique
assert df_alturas_2024["fecha"].is_unique

assert df_2023["fecha"].notna().all()
assert df_2024["fecha"].notna().all()

assert df_alturas_2023["elevacion_solar"].ge(0).all()
assert df_alturas_2024["elevacion_solar"].ge(0).all()

assert len(df_2023) == 525_600
assert len(df_2024) == 527_040
assert len(df_all) == 1_052_640
```

También se recomienda validar:

- igualdad de columnas entre años;
- igualdad de tipos;
- diferencias consecutivas de un minuto;
- ausencia de fechas fuera del periodo;
- rango de mes, día, hora y minuto;
- existencia de los directorios de salida.

## 11. Limitaciones y correcciones pendientes

### 11.1. Registro adicional en la elevación de 2023

El fichero de elevaciones contiene una fila adicional:

```text
2024-01-01 00:00:00
```

con valores ausentes. Actualmente se guarda en el Parquet de 2023. Debe eliminarse antes de la exportación:

```python
df_alturas_2023 = df_alturas_2023[
    df_alturas_2023["fecha"].dt.year == 2023
].copy()
```

Después debe comprobarse:

```python
assert len(df_alturas_2023) == 525_600
```

### 11.2. Inconsistencia del nombre del fichero de elevaciones

El inventario previo utiliza `altura_min_sevilla.xlsx`, mientras que este notebook espera `alturas_2023.xlsx`. Se debe adoptar un único nombre o parametrizar la ruta.

### 11.3. Columnas no reproducibles en la comparación gráfica

La celda gráfica utiliza:

```python
df_solar_2024["date_local"]
```

pero la versión actual del código que genera `df_solar_2024` no crea explícitamente `date_local`. Una ejecución limpia puede producir un `KeyError`.

Debe añadirse:

```python
df_solar_2024["date_local"] = (
    df_solar_2024["timestamp_local"].dt.date
)
```

### 11.4. Convención de `dia`

En el fichero de elevación de 2023, `dia` parece representar el día del año. En los datos de irradiancia, `dia` representa el día del mes.

La documentación y el esquema deben distinguir ambas variables. Se recomienda emplear:

```text
dia_mes
dia_ano
```

o reconstruir ambas a partir de `fecha`:

```python
df["dia_mes"] = df["fecha"].dt.day
df["dia_ano"] = df["fecha"].dt.dayofyear
```

No debe asignarse el mismo nombre a variables con semánticas diferentes.

### 11.5. Zona horaria y cambio horario

El código calcula inicialmente la posición solar con timestamps UTC y crea `timestamp_local`, pero el dataset final vuelve a generar una secuencia UTC sin zona horaria y la combina por posición con los valores calculados.

Por tanto, la convención temporal final debe verificarse frente a los datos de 2023. Es necesario determinar si la columna `fecha` de las mediciones representa:

- UTC;
- hora local civil con cambios DST;
- hora local fija UTC+1;
- otra convención de la estación.

Hasta realizar esta comprobación, la alineación temporal de la elevación solar de 2024 debe considerarse provisional.

### 11.6. Directorio `data/processed`

El notebook crea `data/interim`, pero no crea explícitamente `data/processed`. Antes de guardar debe incluirse:

```python
PROCESSED_PATH = Path("../data/processed")
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
```

### 11.7. Validación incompleta de los datasets anuales

El notebook comprueba duplicados únicamente en la elevación de 2024. Debe validar también:

- mediciones de 2023;
- mediciones de 2024;
- elevación de 2023;
- continuidad minuto a minuto;
- tipos y orden de columnas.

## 12. Ejecución recomendada

Estructura mínima:

```text
project/
├── data/
│   ├── raw/
│   │   ├── datos_2023.xlsx
│   │   ├── datos_2024.xlsx
│   │   └── alturas_2023.xlsx
│   ├── interim/
│   └── processed/
├── notebooks/
│   ├── 01_data_inventory.ipynb
│   └── 02_column_preprocessing.ipynb
└── docs/
```

El notebook debe ejecutarse después del inventario y antes del análisis exploratorio.

## 13. Criterio de finalización

El preprocesamiento de columnas puede considerarse cerrado cuando:

- ambos años tienen nombres y tipos homogéneos;
- se ha eliminado el registro adicional de elevación de 2023;
- la convención temporal está comprobada;
- la variable `dia` tiene una semántica inequívoca;
- las cuatro salidas intermedias se generan sin errores;
- los merges son uno a uno;
- no quedan elevaciones sin asignar;
- el dataset conjunto contiene 1.052.640 registros;
- el notebook se ejecuta completo desde un kernel limpio;
- todas las decisiones quedan registradas en esta documentación.
