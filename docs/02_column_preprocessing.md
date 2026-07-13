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
```

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
