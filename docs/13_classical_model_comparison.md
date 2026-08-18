# 13. Comparación de modelos clásicos de clasificación

## Objetivo

Este notebook realiza una comparación sistemática de modelos clásicos de clasificación para predecir los códigos de calidad de las medidas de irradiancia:

- `codigo_ghi`
- `codigo_dni`
- `codigo_dhi`

El objetivo es comparar distintas familias de algoritmos bajo un mismo esquema de evaluación, analizando previamente el desbalance de las clases, la utilidad de las variables predictoras y las necesidades de preprocesamiento de cada modelo.

La métrica principal de comparación es **Macro F1**, complementada con **Balanced Accuracy**, **Weighted F1** y matrices de confusión.

El `DummyClassifier` calculado previamente se mantiene como referencia mínima y no se repite, ya que sus predicciones no dependen de las variables de entrada.

---

## Dataset de entrada

El notebook utiliza:

```text
../data/processed/dataset_solar_2023_2024_v3.parquet
```

El dataset contiene:

- **1.052.640 registros**
- **27 variables**
- datos correspondientes a **2023 y 2024**
- frecuencia temporal de **un minuto**

---

## Variables objetivo

Los tres códigos presentan un fuerte desbalance de clases.

| Target | Clase 0 | Clase 1 | Clase 2 |
|---|---:|---:|---:|
| `codigo_ghi` | 85,50 % | 14,50 % | — |
| `codigo_dni` | 89,65 % | 10,17 % | 0,18 % |
| `codigo_dhi` | 81,70 % | 18,26 % | 0,04 % |

`codigo_ghi` constituye un problema binario, mientras que `codigo_dni` y `codigo_dhi` son problemas multiclase.

La escasa representación de las clases minoritarias, especialmente la clase 2 de DNI y DHI, justifica utilizar Macro F1 como métrica principal, ya que asigna la misma importancia a todas las clases independientemente de su frecuencia.

También se observan diferencias en la distribución de clases entre 2023 y 2024, con una mayor presencia relativa de clases no mayoritarias en 2024.

---

## Análisis de variables predictoras

Antes del entrenamiento se revisan todas las variables disponibles considerando:

- tipo de dato;
- número de valores únicos;
- valores ausentes;
- utilidad física;
- posible redundancia;
- disponibilidad en un escenario real de predicción.

Las variables `fecha` y `ano` se excluyen desde el inicio como predictores. `fecha` funciona como identificador temporal y `ano` se reserva para definir la separación interanual entre entrenamiento y evaluación.

Las variables se agrupan en:

- temporales;
- irradiancia;
- balance de irradiancia;
- solares;
- meteorológicas;
- calidad de los datos;
- targets.

---

## Valores ausentes

Los valores ausentes se concentran principalmente en:

- variables meteorológicas: aproximadamente **9 %**;
- irradiancias y variables derivadas del balance: aproximadamente **1,13 %**.

Las variables:

- `periodo_solar`
- `irr_null`
- `var_meteo_imp`

se transforman a representación numérica antes del modelado.

La estrategia aplicada a los valores ausentes depende de la capacidad de cada algoritmo para tratarlos.

---

## Relaciones y redundancia entre variables

Se estudia la matriz de correlación como herramienta de diagnóstico.

Las relaciones observadas son coherentes con la naturaleza física del problema: las componentes de irradiancia presentan asociaciones entre sí y con la elevación solar, mientras que las distintas formulaciones del error de balance muestran una elevada redundancia.

Por este motivo se conserva:

```text
error_balance_abs
```

como medida de la magnitud de la incoherencia física entre las componentes de irradiancia.

Se excluyen:

```text
ghi_estimado
error_balance
error_balance_rel
```

para evitar mantener varias representaciones redundantes del mismo fenómeno.

La correlación no se utiliza como criterio automático de eliminación de variables.

---

## Selección final de features

Tras la auditoría se seleccionan **19 variables candidatas**:

```text
mes_sin
mes_cos
dia
hora_sin
hora_cos
minuto
ghi
dni
dhi
error_balance_abs
elevacion_solar
periodo_solar
temperatura
velocidad_viento
humedad_relativa
direccion_viento_sin
direccion_viento_cos
irr_null
var_meteo_imp
```

Las variables meteorológicas pueden ayudar a contextualizar las condiciones en las que se realizan las mediciones, aunque contienen valores ausentes.

`irr_null` conserva información sobre la ausencia original de irradiancia cuando los modelos requieren sustituir esos NaN.

`var_meteo_imp` indica si alguna variable meteorológica ha sido imputada y aporta información sobre la calidad o procedencia del dato.

Los códigos de calidad fueron obtenidos mediante inspección visual, por lo que ninguna de estas variables fue utilizada directamente para generar las etiquetas.

---

## Estrategia de entrenamiento y evaluación

Se utiliza una separación interanual:

```text
Train → 2024
Evaluación interanual → 2023
```

Cada algoritmo se entrena de forma independiente para:

```text
codigo_ghi
codigo_dni
codigo_dhi
```

Se utiliza:

```text
random_state = 42
```

para mantener la reproducibilidad.

Debido al fuerte desbalance de clases, se aplica:

```text
class_weight="balanced"
```

cuando el algoritmo lo permite.

Las métricas utilizadas son:

- **Macro F1**: métrica principal.
- **Balanced Accuracy**: métrica complementaria sensible al rendimiento por clase.
- **Weighted F1**: medida global ponderada por la frecuencia de cada clase.
- **Matriz de confusión**: análisis detallado de los errores por clase.

Además, se representan los aciertos y errores de cada clase para observar directamente el comportamiento sobre las categorías minoritarias.

---

## Preprocesamiento por tipo de modelo

El preprocesamiento se centraliza mediante:

```text
src/preprocessing/model_preprocessing.py
```

y la función:

```python
prepare_model_features()
```

### Modelos sin soporte nativo de NaN

Para Logistic Regression y Random Forest:

- se excluyen las variables meteorológicas con valores ausentes;
- los NaN de `ghi`, `dni`, `dhi` y `error_balance_abs` se sustituyen por `0`;
- se mantiene `irr_null` para distinguir los ceros reales de los registros originalmente ausentes;
- Logistic Regression utiliza estandarización;
- Random Forest mantiene las escalas originales.

Estos modelos utilizan **14 features**.

### Modelos con soporte nativo de NaN

Para HistGradientBoosting:

- se conservan los valores NaN;
- se mantienen las variables meteorológicas;
- se elimina `irr_null`, ya que la ausencia queda representada directamente por el NaN;
- no se aplica estandarización.

HistGradientBoosting utiliza **18 features**.

---

# Modelos evaluados

## Logistic Regression

Logistic Regression se utiliza como referencia lineal.

Configuración principal:

```text
class_weight = balanced
max_iter = 1000
random_state = 42
```

Las variables se estandarizan utilizando exclusivamente los parámetros obtenidos sobre el conjunto de entrenamiento.

### Resultados

| Target | Macro F1 | Balanced Accuracy | Weighted F1 |
|---|---:|---:|---:|
| `codigo_ghi` | **0,6463** | **0,8106** | 0,7901 |
| `codigo_dni` | 0,3580 | **0,7835** | 0,8020 |
| `codigo_dhi` | 0,4131 | 0,5601 | 0,7786 |

Logistic Regression obtiene su mejor comportamiento para GHI. El modelo identifica eficazmente la clase minoritaria, aunque genera un número relevante de falsos positivos.

En DNI mantiene una Balanced Accuracy elevada, pero el Macro F1 disminuye debido al elevado número de errores entre clases. DHI presenta igualmente mayores dificultades, especialmente sobre la clase 2.

---

## Random Forest

Random Forest permite modelar relaciones no lineales e interacciones entre variables sin necesidad de estandarización.

Configuración principal:

```text
class_weight = balanced
random_state = 42
n_jobs = -1
```

El modelo se mantiene sin optimización de hiperparámetros.

### Resultados

| Target | Macro F1 | Balanced Accuracy | Weighted F1 |
|---|---:|---:|---:|
| `codigo_ghi` | 0,5685 | 0,5643 | 0,8247 |
| `codigo_dni` | 0,4890 | 0,5511 | 0,9275 |
| `codigo_dhi` | 0,4505 | 0,5050 | 0,8470 |

Random Forest empeora respecto a Logistic Regression en GHI, pero mejora los resultados de Macro F1 en DNI y DHI.

Las matrices de confusión evidencian dificultades para las clases extremadamente minoritarias. En particular, no se clasifica correctamente ninguna observación de la clase 2 de DHI.

---

## HistGradient Boosting

HistGradientBoosting se utiliza por su capacidad para modelar relaciones no lineales y trabajar directamente con valores ausentes.

Configuración principal:

```text
class_weight = balanced
random_state = 42
```

No se realiza estandarización ni optimización de hiperparámetros.

### Resultados

| Target | Macro F1 | Balanced Accuracy | Weighted F1 |
|---|---:|---:|---:|
| `codigo_ghi` | 0,6158 | 0,6100 | 0,8428 |
| `codigo_dni` | **0,5347** | 0,6256 | **0,9409** |
| `codigo_dhi` | **0,4787** | 0,5559 | **0,8632** |

HistGradientBoosting no supera a Logistic Regression en GHI, pero obtiene el mejor Macro F1 de los modelos analizados para DNI y DHI.

DHI continúa siendo el problema más difícil. La clase 2, extremadamente minoritaria, no es correctamente identificada por el modelo.

---

## Comparación global

La comparación mediante Macro F1 es:

| Modelo | Nº features | GHI | DNI | DHI |
|---|---:|---:|---:|---:|
| HistGradientBoosting | 18 | 0,6158 | **0,5347** | **0,4787** |
| LogisticRegression | 14 | **0,6463** | 0,3580 | 0,4131 |
| RandomForest | 14 | 0,5685 | 0,4890 | 0,4505 |

Los candidatos más prometedores en esta fase son:

```text
GHI → Logistic Regression
DNI → HistGradientBoosting
DHI → HistGradientBoosting
```

Esta selección es únicamente provisional, ya que todavía deben compararse con las familias de modelos previstas en las siguientes etapas del proyecto.

---

## Conclusiones

La comparación confirma que no existe un único algoritmo claramente superior para los tres códigos de calidad.

Logistic Regression obtiene el mejor resultado para GHI, mientras que HistGradientBoosting presenta el mejor rendimiento en DNI y DHI. Random Forest no alcanza el mejor Macro F1 en ninguno de los targets, aunque mejora a Logistic Regression en los dos problemas multiclase.

Las diferencias entre Macro F1 y Weighted F1 confirman que el fuerte desbalance condiciona significativamente la evaluación. Las clases 2 de DNI y, especialmente, DHI constituyen el principal reto del problema de clasificación.

Estos resultados representan una comparación inicial **sin optimización de hiperparámetros**, manteniendo únicamente el tratamiento explícito del desbalance mediante `class_weight="balanced"` cuando el algoritmo lo permite.

La evaluación realizada sobre 2023 se considera una **evaluación interanual**. La selección y ajuste posterior de hiperparámetros deberá realizarse utilizando únicamente los datos de entrenamiento de 2024 para evitar adaptar los modelos al conjunto de evaluación.

Antes de seleccionar la solución definitiva se incorporarán los modelos previstos en las siguientes etapas del proyecto, incluyendo Deep Learning y procesamiento mediante Spark. Posteriormente, los candidatos más prometedores serán optimizados y comparados en la fase final de modelado.

---

## Funciones reutilizadas

El notebook reutiliza las funciones definidas en:

```text
src/evaluation/evaluation.py
```

para:

- cálculo de métricas;
- matrices de confusión;
- análisis de predicciones correctas e incorrectas por clase;
- creación de la tabla comparativa de modelos.

También utiliza:

```text
src/preprocessing/model_preprocessing.py
```

para centralizar el preprocesamiento específico de cada familia de modelos.

---

## Archivos relacionados

```text
data/processed/dataset_solar_2023_2024_v3.parquet
src/evaluation/evaluation.py
src/preprocessing/model_preprocessing.py
notebooks/12_...
notebooks/13_classical_model_comparison.ipynb
```

El notebook no genera una nueva versión del dataset. Su resultado principal es la comparación reproducible de los modelos clásicos y la identificación provisional de candidatos para las siguientes fases de modelado.

---

## Persistencia de resultados

Una vez finalizado el análisis y extraídas las conclusiones del notebook, los resultados se persisten para que puedan reutilizarse en las siguientes etapas del proyecto sin necesidad de repetir el entrenamiento.

La persistencia se divide entre PostgreSQL y MongoDB según la naturaleza de la información:

- **PostgreSQL** almacena la información estructurada de cada modelo, sus variables de entrada, hiperparámetros y métricas globales de evaluación.
- **MongoDB** incorpora a los documentos diarios de `daily_summaries` un resumen de las predicciones realizadas sobre 2023.

Esta separación mantiene las métricas y metadatos tabulares en la capa relacional y utiliza MongoDB como capa documental para enriquecer los resúmenes diarios.

### PostgreSQL

Los resultados de Logistic Regression, Random Forest e HistGradientBoosting se registran utilizando la versión `v3` del dataset.

Para cada combinación modelo-target se conserva:

```text
dataset_version_id
model_name
target
train_year
test_year
n_features
features
hyperparameters
f1_macro
balanced_accuracy
f1_weighted
```

La inserción se realiza de forma transaccional y devuelve el `model_id` asignado a cada combinación. Este identificador permite relacionar posteriormente los resultados almacenados en PostgreSQL con los resúmenes documentales de MongoDB.

El `DummyClassifier` no se vuelve a registrar en este notebook, ya que pertenece al análisis baseline realizado previamente.

### MongoDB

La colección `daily_summaries` ya contiene un documento por cada fecha y versión del dataset. Para las fechas de 2023 se añade información de los modelos evaluados dentro del bloque reservado para resultados de modelado.

Cada ejecución diaria incluye:

```text
model_id
modelo
target
dataset_version
train_year
test_year
n_features
n_observaciones
aciertos
errores
clases
distribucion_real
distribucion_predicha
matriz_confusion
```

No se almacenan nuevamente todas las predicciones minuto a minuto en MongoDB. En su lugar, cada documento conserva un resumen diario y una referencia mediante `model_id` a la información estructurada del modelo en PostgreSQL.

La actualización se realiza sobre los documentos ya existentes y de forma idempotente: si una ejecución con el mismo `model_id` ya existe para una fecha, se sustituye en lugar de duplicarse.

### Resultado esperado de la persistencia

La persistencia está diseñada para dejar los resultados del notebook disponibles en dos capas complementarias:

```text
PostgreSQL
├── configuración del modelo
├── variables utilizadas
├── hiperparámetros
└── métricas globales

MongoDB
└── daily_summaries
    └── resultados_modelos
        └── ejecuciones
            └── resumen diario por modelo y target
```

La validación final de este bloque debe realizarse a partir de la salida real de las funciones de persistencia, comprobando el número de experimentos almacenados en PostgreSQL y el número de días procesados correctamente o con error en MongoDB.

Una vez verificada la ejecución, estos resultados podrán reutilizarse en las siguientes fases del proyecto sin necesidad de repetir los entrenamientos realizados en este notebook.
