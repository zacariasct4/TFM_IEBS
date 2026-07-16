# 03 — Análisis exploratorio inicial

## Descripción

El notebook `03_initial_eda.ipynb` realiza el análisis exploratorio inicial del conjunto de datos consolidado de irradiancia solar correspondiente a 2023 y 2024.

El análisis estudia la estructura y calidad del dataset, la distribución de las variables, los patrones temporales, los valores ausentes, los códigos de calidad de las irradiancias y la coherencia física entre las componentes GHI, DNI y DHI.

Además, se generan variables derivadas basadas en la ecuación de cierre de la irradiancia solar que podrán utilizarse posteriormente durante la ingeniería de características y el modelado.

---

## Objetivos

Los objetivos principales del notebook son:

- Validar la estructura temporal y la integridad general del dataset.
- Analizar la distribución de las variables de irradiancia y meteorológicas.
- Estudiar los patrones de valores ausentes.
- Comparar el comportamiento de los datos de 2023 y 2024.
- Diferenciar los registros correspondientes al periodo diurno y nocturno.
- Analizar la distribución de los códigos de calidad de GHI, DNI y DHI.
- Comprobar la coherencia física entre las tres componentes de irradiancia.
- Evaluar la relación entre el error de balance físico y los códigos de calidad.
- Preparar nuevas variables físicas para etapas posteriores del proyecto.

---

## Archivo de entrada

El notebook carga el siguiente archivo:

```text
../data/processed/dataset_solar_2023_2024_v1.parquet
```

El dataset inicial contiene:

- **1.052.640 registros**, correspondientes a mediciones por minuto de 2023 y 2024.
- **20 variables iniciales**.
- Una serie temporal completa desde el **1 de enero de 2023** hasta el **31 de diciembre de 2024**.
- **525.600 registros** para 2023.
- **527.040 registros** para 2024.
- Ninguna fecha duplicada.
- Ningún minuto ausente respecto al número esperado para ambos años.

---

## Librerías utilizadas

```python
pandas
numpy
matplotlib
seaborn
scikit-learn
```

Las métricas de evaluación se obtienen mediante:

```python
sklearn.metrics.roc_auc_score
sklearn.metrics.average_precision_score
```

---

## Estructura del análisis

### 1. Validación inicial del dataset

Se comprueban:

- Dimensiones del conjunto de datos.
- Tipos de las variables.
- Rango temporal.
- Duplicados en la columna `fecha`.
- Número real y esperado de muestras por año.
- Disponibilidad general de los datos.

La serie temporal contiene exactamente una observación por minuto durante los dos años analizados.

---

### 2. Análisis de valores ausentes

Se estudian los patrones conjuntos de ausencia de las variables numéricas.

Los principales grupos identificados son:

- **957.464 registros completos**.
- **83.308 registros** con irradiancias y elevación solar disponibles, pero con ausencia simultánea de las variables meteorológicas.
- **11.868 registros** en los que únicamente permanece disponible la elevación solar.

Los valores ausentes no aparecen de forma aleatoria. Las tres irradiancias tienden a faltar simultáneamente y las variables meteorológicas presentan otro patrón conjunto de ausencia.

También se analiza específicamente la relación entre la ausencia de `dni` y `codigo_dni`. La mayor proporción de valores ausentes de DNI se concentra en los registros con código 1.

---

### 3. Creación del periodo solar

Se genera la variable categórica `periodo_solar` a partir de la elevación solar:

```python
df["periodo_solar"] = np.where(
    df["elevacion_solar"] > 0,
    "dia",
    "noche"
)
```

Esta variable permite separar los registros en:

- `dia`: elevación solar positiva.
- `noche`: elevación solar igual o inferior a cero.

La separación resulta necesaria porque las irradiancias presentan comportamientos físicos diferentes durante ambos periodos.

---

### 4. Análisis descriptivo de las variables

Se calculan estadísticas descriptivas y se representan histogramas y diagramas de caja diferenciados por periodo solar.

Las variables analizadas son:

- `ghi`
- `dni`
- `dhi`
- `elevacion_solar`
- `temperatura`
- `velocidad_viento`
- `direccion_viento_sin`
- `direccion_viento_cos`
- `humedad_relativa`

Los resultados muestran:

- Una fuerte concentración de las irradiancias en cero durante la noche.
- Distribuciones asimétricas y con valores extremos durante el día.
- Valores máximos de GHI y DHI que deben considerarse potencialmente anómalos.
- Un valor mínimo de temperatura de −50 °C, probablemente asociado a una medición o codificación incorrecta.
- Una distribución asimétrica de la velocidad del viento, dominada por velocidades bajas.
- Mayor humedad relativa durante la noche y mayor temperatura durante el día.
- Diferencias claras entre los periodos diurno y nocturno.

---

### 5. Análisis de los códigos de calidad

Se estudian las variables:

- `codigo_ghi`
- `codigo_dni`
- `codigo_dhi`

El código 0 es mayoritario en las tres irradiancias, aunque su proporción disminuye en 2024.

Los principales resultados son:

- Aumento de los registros con código 1 en 2024.
- Incremento especialmente relevante en `codigo_dhi`.
- Mayor presencia de incidencias durante los periodos nocturnos de 2024.
- Presencia residual del código 2.
- Mayor frecuencia de la combinación simultánea `(1, 1, 1)` durante 2024.

Las combinaciones de códigos se representan separadamente para cada año y periodo solar.

---

### 6. Correlaciones entre variables

Se calculan matrices de correlación de Pearson para las variables numéricas continuas, separando:

- Registros diurnos.
- Registros nocturnos.

Durante el día, las irradiancias presentan correlaciones positivas entre sí y con la elevación solar. Destacan especialmente las relaciones entre GHI y DNI y entre GHI y elevación solar.

La temperatura y la humedad relativa presentan una correlación negativa elevada.

Las correlaciones nocturnas deben interpretarse con cautela debido a la elevada concentración de irradiancias iguales a cero.

---

### 7. Patrones mensuales y horarios

La función `features_per_time` calcula y representa las medias de las variables por:

- Mes.
- Hora.
- Periodo solar.
- Año.

El análisis se ejecuta independientemente para 2023 y 2024.

Las irradiancias siguen el patrón diario esperado:

1. Valores próximos a cero durante la noche.
2. Incremento después del amanecer.
3. Máximos durante las horas centrales.
4. Descenso hacia el atardecer.

Se identifican dos periodos que requieren especial atención:

- Una caída de GHI durante mayo de 2023.
- Una reducción simultánea de GHI, DNI y DHI durante septiembre de 2024.

---

### 8. Comparación estadística entre años

La comparación de las irradiancias durante el periodo diurno muestra:

| Variable | Media 2023 | Media 2024 | Variación |
|---|---:|---:|---:|
| GHI | 338,59 W/m² | 368,84 W/m² | +8,93 % |
| DNI | 489,28 W/m² | 417,89 W/m² | −14,59 % |
| DHI | 153,97 W/m² | 124,00 W/m² | −19,47 % |

Estas diferencias describen cambios en las distribuciones de las irradiancias, pero no permiten atribuirlos directamente a una causa meteorológica concreta.

La ecuación física debe comprobarse registro a registro, ya que la contribución horizontal del DNI depende de la elevación solar de cada instante.

---

### 9. Análisis temporal de valores ausentes

Las funciones `analyze_missing_values` y `analyze_missing_temporal_patterns` estudian los nulos por:

- Año.
- Periodo solar.
- Mes.
- Hora.
- Tipo de variable.

Los principales resultados son:

- En 2023, las variables meteorológicas presentan aproximadamente un 4 % de nulos.
- En 2024, la proporción aumenta hasta aproximadamente un 14–15 %.
- Los meses con mayor ausencia de datos en 2023 son marzo, abril, julio y diciembre.
- En 2024 destacan marzo y septiembre.
- La elevación solar está disponible para todos los registros.
- Las irradiancias faltan simultáneamente.
- Las variables meteorológicas también presentan un patrón conjunto de ausencia.

---

## Coherencia física de las irradiancias

### Ecuación de cierre

La coherencia entre las tres componentes se evalúa mediante:

\[
GHI = DHI + DNI \cdot \max(\sin(\alpha), 0)
\]

donde:

- `GHI` es la irradiancia global horizontal.
- `DHI` es la irradiancia difusa horizontal.
- `DNI` es la irradiancia directa normal.
- `α` es la elevación solar.

La función `max` evita obtener una componente directa horizontal negativa cuando el Sol está bajo el horizonte.

---

### Variables físicas generadas

#### `ghi_estimado`

Reconstrucción de GHI mediante DNI, DHI y elevación solar:

```python
sin_elevacion = np.sin(
    np.radians(df["elevacion_solar"])
).clip(lower=0)

df["ghi_estimado"] = (
    df["dhi"]
    + df["dni"] * sin_elevacion
)
```

#### `error_balance`

Diferencia firmada entre la GHI medida y la reconstruida:

```python
df["error_balance"] = (
    df["ghi"] - df["ghi_estimado"]
)
```

Interpretación:

- Valor positivo: la GHI medida es superior a la reconstruida.
- Valor negativo: la GHI reconstruida es superior a la medida.

#### `error_balance_abs`

Magnitud absoluta del error:

```python
df["error_balance_abs"] = (
    df["error_balance"].abs()
)
```

#### `error_balance_rel`

Error regularizado respecto a GHI:

```python
df["error_balance_rel"] = (
    df["error_balance_abs"]
    / df["ghi"].abs().clip(lower=10)
)
```

El denominador mínimo de 10 W/m² evita cocientes extremadamente elevados cuando GHI es próxima a cero. Por tanto, esta variable debe interpretarse como un **error relativo regularizado**, no como un error relativo convencional.

---

## Resultados del balance físico

La distribución del error presenta:

- Mediana del error absoluto igual a cero.
- Error firmado medio de aproximadamente −27,57 W/m².
- Fuerte asimetría.
- Una cola de errores negativos de gran magnitud.
- Diferencias importantes entre el comportamiento diurno y nocturno.

La concentración de errores iguales a cero se debe principalmente a los registros nocturnos.

Durante el día:

- El error absoluto medio es de aproximadamente **84,77 W/m²**.
- La mediana es de aproximadamente **12,66 W/m²**.
- Los errores elevados se concentran en una proporción limitada de registros.

Durante la noche:

- El error absoluto medio es de aproximadamente **0,10 W/m²**.
- La mediana y los percentiles superiores principales son iguales a cero.

---

## Balance físico y códigos de calidad

El error de balance se compara con los códigos de GHI, DNI y DHI.

Los resultados indican:

- Los registros con `codigo_ghi = 1` presentan una cola de errores mucho mayor que los registros con código 0.
- Los registros con `codigo_dhi = 1` también presentan errores absolutos considerablemente superiores.
- Para DNI se observa el comportamiento contrario: los códigos incorrectos tienden a presentar errores de balance menores.

Por tanto, el error de cierre puede aportar información sobre la calidad de GHI y DHI, pero no funciona de la misma manera para DNI.

---

## Comparación del balance entre años

El balance físico presenta diferencias relevantes entre 2023 y 2024:

- Error absoluto medio en 2023: **60,89 W/m²**.
- Error absoluto medio en 2024: **24,43 W/m²**.
- Reducción aproximada: **59,87 %**.
- Mayor dispersión y una cola de valores extremos más elevada en 2023.
- Error firmado medio de −52,71 W/m² en 2023 y −2,09 W/m² en 2024.

Las principales diferencias interanuales están asociadas a episodios concretos de gran magnitud y no al comportamiento del registro típico.

---

## Capacidad discriminante del error de balance

Para evaluar si `error_balance_abs` puede diferenciar registros correctos e incorrectos, los códigos se transforman temporalmente en variables binarias:

```text
0 → correcto
1 → código original distinto de 0
```

Las métricas se calculan únicamente sobre registros que disponen simultáneamente de:

- GHI.
- DNI.
- DHI.
- Elevación solar.

Resultados principales:

| Target | ROC-AUC aproximado | Interpretación |
|---|---:|---|
| `codigo_ghi` | 0,515 | Capacidad global débil |
| `codigo_dni` | 0,310 | Asociación inversa |
| `codigo_dhi` | 0,550 | Capacidad débil, pero superior a GHI |

El error absoluto no permite separar por sí solo todos los registros correctos e incorrectos.

En GHI y DHI, los valores extremos contienen cierta información discriminante. Para DNI, los registros incorrectos tienden a presentar errores más bajos, por lo que un error elevado no funciona como indicador directo.

---

## Funciones definidas

### `plot_hist_box`

Genera histogramas y diagramas de caja de las variables numéricas, diferenciando entre día y noche.

### `features_per_time`

Calcula las medias mensuales y horarias para un año concreto y representa los resultados por periodo solar.

### `analyze_missing_values`

Analiza la proporción de valores ausentes y la correlación entre patrones de ausencia, separando año y periodo solar.

### `analyze_missing_temporal_patterns`

Estudia la evolución de los valores ausentes por mes y hora.

---

## Variables temporales auxiliares

Durante el análisis se crean temporalmente:

- `mes`
- `hora`
- `codigo_ghi_incorrecto`
- `codigo_dni_incorrecto`
- `codigo_dhi_incorrecto`
- `balance_disponible`

Estas variables se utilizan para los cálculos y gráficos, pero no se incluyen en la selección final de columnas del `DataFrame`.

---

## Estructura final del DataFrame

Al finalizar el notebook, las columnas se ordenan de la siguiente forma:

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
ghi_estimado
error_balance
error_balance_abs
error_balance_rel
elevacion_solar
periodo_solar
temperatura
velocidad_viento
humedad_relativa
direccion_viento_sin
direccion_viento_cos
codigo_ghi
codigo_dni
codigo_dhi
```

Al finalizar el notebook, el `DataFrame` se reorganiza con las variables temporales, meteorológicas, físicas y de calidad seleccionadas. Posteriormente, el conjunto de datos enriquecido se exporta en formato Parquet para su utilización en las siguientes etapas del proyecto.


---

## Archivo de salida

El notebook genera el siguiente archivo:

```text
../data/processed/dataset_solar_2023_2024_v2.parquet
```

La exportación se realiza mediante:

```python
df.to_parquet(
    "../data/processed/dataset_solar_2023_2024_v2.parquet",
    index=False
)
```

El parámetro `index=False` evita almacenar el índice interno de pandas como una columna adicional.

El archivo `dataset_solar_2023_2024_v2.parquet` contiene el conjunto de datos consolidado y enriquecido con las siguientes variables generadas durante el análisis:

* `periodo_solar`
* `ghi_estimado`
* `error_balance`
* `error_balance_abs`
* `error_balance_rel`

Este archivo constituye la segunda versión procesada del dataset y se utilizará como entrada para las siguientes etapas del proyecto:

* Ingeniería de características.
* Preparación de las etiquetas de clasificación.
* Detección de anomalías.
* Entrenamiento y evaluación de modelos.
* Procesamiento mediante PostgreSQL y PySpark.


---

## Ejecución

El notebook debe ejecutarse después de completar:

1. El inventario y consolidación de los archivos de origen.
2. La normalización y preprocesamiento de columnas.
3. La generación del archivo:

```text
dataset_solar_2023_2024_v1.parquet
```

La ruta relativa presupone que el notebook se ejecuta desde la carpeta `notebooks/` de la estructura del proyecto.

Tras completar correctamente todas las celdas, el notebook guarda el resultado en:

```text
data/processed/dataset_solar_2023_2024_v2.parquet
```

La existencia de este archivo debe comprobarse antes de ejecutar los notebooks posteriores que dependan de las variables físicas generadas durante el análisis exploratorio.


---

## Conclusión

El análisis confirma que el dataset presenta una estructura temporal completa, pero contiene patrones de ausencia, valores extremos y diferencias relevantes entre años y periodos solares.

La incorporación de la ecuación física de cierre permite generar variables capaces de describir inconsistencias entre GHI, DNI y DHI. Aunque el error de balance no permite clasificar por sí solo la calidad de todas las irradiancias, aporta información útil para GHI y DHI y constituye una característica relevante para las siguientes etapas del proyecto.
