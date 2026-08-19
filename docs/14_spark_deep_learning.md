# Notebook 14 — Procesamiento con Spark y Deep Learning

## Objetivo

Este notebook amplía el pipeline de modelado mediante dos componentes:

- **Apache Spark**, utilizado para la carga, transformación y particionado inicial del dataset.
- **TensorFlow/Keras**, utilizado para entrenar una red neuronal multicapa (MLP) independiente para cada código de calidad: `codigo_ghi`, `codigo_dni` y `codigo_dhi`.

Se mantiene el marco experimental definido previamente: **2024 como periodo de desarrollo del modelo y 2023 como test externo**, utilizando **Macro F1** como métrica principal y Balanced Accuracy y Weighted F1 como métricas complementarias.

---

## Datos de entrada

Dataset utilizado:

`data/processed/dataset_solar_2023_2024_v3.parquet`

Dimensiones:

- **1.052.640 registros**
- **27 variables**
- 2024: **527.040 registros**
- 2023: **525.600 registros**

Spark conserva correctamente los tipos numéricos, temporales, booleanos y categóricos definidos durante las fases anteriores del proyecto.

---

## Procesamiento con Spark

El dataset se carga directamente desde Parquet mediante un `SparkDataFrame`.

Las principales operaciones realizadas con Spark son:

1. Validación del esquema y de las columnas necesarias.
2. Separación temporal:
   - **Train/desarrollo:** 2024.
   - **Test externo:** 2023.
3. Análisis de la distribución de los tres targets por año.
4. Conversión de variables booleanas y categóricas a representación numérica.
5. División temporal interna de 2024 en entrenamiento y validación.
6. Selección de las columnas necesarias antes de la conversión a Pandas.

Las distribuciones muestran un fuerte desbalance de clases, especialmente en `codigo_dni`, así como diferencias relevantes entre 2023 y 2024. Por este motivo se mantiene **Macro F1** como métrica decisoria.

---

## Variables utilizadas

Se parte de **19 features candidatas**, excluyendo:

- `ano`
- `fecha`
- `ghi_estimado`
- `error_balance`
- `error_balance_rel`
- los tres targets

La preparación final reutiliza la función común `prepare_model_features()`, con:

- `accepts_nan=False`
- `scale=True`

Tras aplicar el tratamiento de valores ausentes, se utilizan finalmente **14 features**:

- `mes_sin`
- `mes_cos`
- `dia`
- `hora_sin`
- `hora_cos`
- `minuto`
- `ghi`
- `dni`
- `dhi`
- `irr_null`
- `error_balance_abs`
- `elevacion_solar`
- `periodo_solar`
- `var_meteo_imp`

Las variables se estandarizan mediante `StandardScaler`, ajustado exclusivamente sobre el subconjunto de entrenamiento interno.

---

## División entrenamiento-validación

Dentro de 2024 se reserva temporalmente el **20 % final** como validación:

- Entrenamiento interno: **421.512 registros**
- Validación: **105.528 registros**
- Test externo 2023: **525.600 registros**

La división se realiza temporalmente para evitar mezclar aleatoriamente observaciones consecutivas de una serie minuto a minuto.

Las distribuciones de clases no son idénticas entre entrenamiento y validación debido al carácter temporal del corte, por lo que la validación interna se utiliza principalmente para controlar el entrenamiento y seleccionar la mejor época.

---

## Modelado MLP

Se entrena una red neuronal independiente para cada target.

La arquitectura común contiene:

- Capa de entrada.
- Capa densa de **64 neuronas**, activación ReLU.
- Capa densa de **32 neuronas**, activación ReLU.
- Capa de salida adaptada automáticamente:
  - clasificación binaria para `codigo_ghi`;
  - clasificación multiclase para `codigo_dni` y `codigo_dhi`.

Configuración principal:

- Optimizador: **Adam**
- Learning rate: **0.001**
- Batch size: **256**
- Máximo de épocas: **100**
- Compensación del desbalance mediante **class weights**
- `EarlyStopping` monitorizando **`val_macro_f1`**
- Restauración de los pesos correspondientes a la mejor época

La arquitectura se mantiene deliberadamente compacta para comprobar si el uso de Deep Learning aporta suficiente valor antes de justificar modelos de mayor complejidad.

---

## Resultados de validación

| Target | Mejor época | Mejor Macro F1 validación |
|---|---:|---:|
| `codigo_ghi` | 3 | 0,474 |
| `codigo_dni` | 29 | 0,343 |
| `codigo_dhi` | 4 | 0,484 |

En GHI se observa una reducción continua de la pérdida de entrenamiento mientras aumenta la pérdida de validación, indicando **sobreajuste temprano en términos probabilísticos**. Sin embargo, el Macro F1 mejora ligeramente durante las primeras épocas y alcanza su máximo en la época 3, que es la seleccionada al ser la métrica principal del proyecto.

Dado el rendimiento limitado de la validación, no se realiza una optimización específica adicional de la MLP.

---

## Evaluación sobre 2023

Los modelos correspondientes a la mejor época de validación se evalúan sobre el test externo de 2023.

| Target | Features | Macro F1 | Balanced Accuracy | Weighted F1 |
|---|---:|---:|---:|---:|
| `codigo_ghi` | 14 | **0,744** | 0,782 | 0,884 |
| `codigo_dni` | 14 | **0,463** | 0,676 | 0,904 |
| `codigo_dhi` | 14 | **0,451** | 0,515 | 0,843 |

GHI presenta el mejor comportamiento global. DNI y DHI obtienen valores de Weighted F1 elevados, pero sus Macro F1 son considerablemente inferiores, evidenciando el efecto del fuerte desbalance de clases.

Las matrices de confusión y los gráficos de aciertos y errores por clase muestran que los modelos funcionan mejor sobre las clases mayoritarias y presentan mayores dificultades sobre las clases menos frecuentes.

---

## Persistencia de resultados

Los resultados de la MLP se almacenan siguiendo la misma arquitectura utilizada para los modelos anteriores.

### PostgreSQL

Se registran:

- configuración del modelo;
- versión del dataset;
- años de entrenamiento y test;
- features utilizadas;
- hiperparámetros;
- métricas globales de cada target.

Los modelos MLP quedaron registrados con los siguientes identificadores:

- `codigo_ghi` → `model_id = 22`
- `codigo_dni` → `model_id = 23`
- `codigo_dhi` → `model_id = 24`

### MongoDB

Las predicciones minuto a minuto del test de 2023 se agrupan por fecha y se incorporan a los documentos `daily_summaries`.

Para cada día y target se almacenan:

- referencia al `model_id` de PostgreSQL;
- métricas diarias;
- distribución real de clases;
- distribución predicha;
- matriz de confusión diaria;
- información del experimento.

Resultado de la persistencia:

- **365 días procesados correctamente**
- **0 errores**

De esta forma, PostgreSQL conserva la información estructurada y global de los modelos, mientras que MongoDB mantiene el detalle temporal de sus resultados.

---

## Conclusiones

Spark se integra de forma funcional en el pipeline para realizar la carga, transformación y particionado inicial de más de un millón de observaciones antes del modelado con TensorFlow.

La arquitectura MLP obtiene un comportamiento razonable para GHI, pero presenta resultados limitados en DNI y DHI al considerar la métrica principal Macro F1. Además, se detecta sobreajuste temprano y una sensibilidad relevante al fuerte desbalance de clases.

Por tanto, **no se considera justificado aumentar la complejidad del enfoque mediante un proceso específico de optimización de la MLP**. El experimento queda registrado como alternativa de Deep Learning y sus resultados quedan disponibles en PostgreSQL y MongoDB para su comparación posterior con los modelos clásicos en el siguiente notebook.
