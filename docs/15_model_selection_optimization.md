# 15. Optimización y selección de modelos finales

## Objetivo

Este notebook consolida la fase final de modelado del proyecto. Parte de los experimentos realizados previamente para los tres códigos de calidad de irradiancia (`codigo_ghi`, `codigo_dni` y `codigo_dhi`), recupera sus configuraciones y resultados desde PostgreSQL, optimiza los candidatos seleccionados y establece un modelo definitivo para cada target.

La estrategia de evaluación mantiene una separación temporal entre años:

- **2024** se utiliza para el ajuste y la optimización de hiperparámetros.
- **2023** se utiliza como referencia interanual para comparar las configuraciones finales con los resultados obtenidos previamente.

La métrica principal de selección es **Macro F1**, ya que permite valorar de forma equilibrada el rendimiento sobre clases con frecuencias muy diferentes. Como métricas complementarias se utilizan **Balanced Accuracy** y **Weighted F1**.

Para GHI se realiza además una comparación temporal homogénea entre Logistic Regression y MLP, con el objetivo de reducir la dependencia de una única partición de validación.

---

## Dataset de entrada

El notebook utiliza como entrada:

```text
../data/processed/dataset_solar_2023_2024_v3.parquet
```

El dataset contiene **1.052.640 registros y 27 variables**, con información minuto a minuto correspondiente a 2023 y 2024.

Las variables objetivo son:

```text
codigo_ghi
codigo_dni
codigo_dhi
```

Durante el modelado se excluyen de las variables predictoras:

```text
fecha
ano
codigo_ghi
codigo_dni
codigo_dhi
```

Las features concretas utilizadas por cada modelo se recuperan desde los experimentos almacenados previamente en PostgreSQL.

---

## Recuperación de experimentos previos

Los resultados de la fase anterior de modelado se consultan desde las tablas:

```text
solar.models
solar.results
```

Para cada experimento se recuperan, entre otros elementos:

- identificador del modelo;
- nombre del algoritmo;
- target;
- número y listado de features;
- hiperparámetros;
- Macro F1;
- Balanced Accuracy;
- Weighted F1.

Los principales candidatos de partida son:

| Target | Modelo candidato | Macro F1 previo |
|---|---|---:|
| `codigo_ghi` | MLP | 0,7435 |
| `codigo_ghi` | Logistic Regression | 0,6463 |
| `codigo_dni` | HistGradientBoosting | 0,5347 |
| `codigo_dhi` | HistGradientBoostingClassifier | 0,4986 |

Para GHI se mantienen tanto MLP como Logistic Regression, ya que la red neuronal había mostrado un rendimiento superior pero también una mayor sensibilidad al proceso de entrenamiento.

En los experimentos anteriores aparecen las etiquetas `HistGradientBoosting` y `HistGradientBoostingClassifier`. En la selección definitiva se utiliza el nombre completo `HistGradientBoostingClassifier`.

---

## Validación interna sobre 2024

La optimización de hiperparámetros se realiza exclusivamente con registros de 2024.

Antes de definir la partición se analiza la presencia mensual de las clases para evitar seleccionar meses que eliminen alguna clase del conjunto de entrenamiento o validación.

Se utiliza inicialmente la siguiente separación:

```text
Meses de validación: marzo, agosto y noviembre
Resto de 2024: entrenamiento
```

El resultado es:

```text
Entrenamiento: 394.560 registros
Validación:    132.480 registros
Total 2024:    527.040 registros
```

Los tres targets conservan todas sus clases tanto en entrenamiento como en validación.

La variable auxiliar `mes_validation` se utiliza únicamente para construir las particiones temporales y no forma parte de las features de los modelos.

---

## Preprocesamiento específico por modelo

Las features seleccionadas para cada candidato se preparan mediante una función común de preprocesamiento.

Antes del modelado:

- las variables booleanas se convierten a valores numéricos;
- `periodo_solar` se codifica numéricamente;
- se comprueba que no permanezcan variables categóricas sin transformar.

El tratamiento posterior depende del algoritmo:

### MLP y Logistic Regression

- No admiten valores nulos.
- Utilizan únicamente las filas válidas para las features seleccionadas.
- Las variables se estandarizan mediante `StandardScaler`.

### HistGradientBoostingClassifier

- Admite valores nulos de forma nativa.
- No requiere estandarización.

El scaler se ajusta siempre utilizando exclusivamente los datos de entrenamiento de cada partición.

---

## Optimización de HistGradientBoostingClassifier

Para DNI y DHI se realiza una búsqueda aleatoria de hiperparámetros.

El espacio de búsqueda incluye:

- `learning_rate`;
- `max_iter`;
- `max_leaf_nodes`;
- `max_depth`;
- `min_samples_leaf`;
- `l2_regularization`.

Cada configuración se evalúa mediante:

- Macro F1 de entrenamiento;
- Macro F1 de validación;
- gap entre entrenamiento y validación;
- Balanced Accuracy;
- Weighted F1;
- tiempo de entrenamiento.

Los resultados se guardan para evitar repetir la búsqueda en ejecuciones posteriores.

### DNI

La mejor configuración obtiene:

| Métrica | Resultado |
|---|---:|
| Macro F1 validación | 0,6747 |
| Macro F1 entrenamiento | 0,7763 |
| Gap | 0,1016 |
| Balanced Accuracy | 0,6752 |
| Weighted F1 | 0,9758 |

Hiperparámetros seleccionados:

```text
learning_rate = 0.08
max_iter = 500
max_leaf_nodes = 31
max_depth = 5
min_samples_leaf = 40
l2_regularization = 0.0
```

### DHI

La mejor configuración obtiene:

| Métrica | Resultado |
|---|---:|
| Macro F1 validación | 0,5734 |
| Macro F1 entrenamiento | 0,6612 |
| Gap | 0,0877 |
| Balanced Accuracy | 0,5617 |
| Weighted F1 | 0,8874 |

Hiperparámetros seleccionados:

```text
learning_rate = 0.15
max_iter = 500
max_leaf_nodes = 63
max_depth = 5
min_samples_leaf = 10
l2_regularization = 0.0
```

Los valores de Weighted F1 son considerablemente superiores a Macro F1, especialmente en DNI, lo que confirma el efecto del desequilibrio entre clases y justifica mantener Macro F1 como criterio principal.

---

## Optimización de los candidatos para GHI

Para GHI se optimizan Logistic Regression y MLP.

La primera partición temporal se utiliza como **screening inicial** de configuraciones. Posteriormente, los mejores candidatos de ambos algoritmos se someten a una validación temporal común.

### Logistic Regression: screening inicial

Se exploran combinaciones de:

- solver `lbfgs` y `liblinear`;
- regularización L1 y L2;
- diferentes valores de `C`;
- `class_weight=None` y `class_weight="balanced"`.

La mejor configuración inicial obtiene:

| Métrica | Resultado |
|---|---:|
| Macro F1 validación | 0,6785 |
| Macro F1 entrenamiento | 0,6555 |
| Balanced Accuracy | 0,6427 |
| Weighted F1 | 0,8175 |

Configuración:

```text
solver = liblinear
penalty = l2
C = 0.0081
class_weight = None
max_iter = 1000
```

Este resultado se utiliza únicamente como screening inicial.

---

## Optimización inicial del MLP

El MLP se optimiza explorando:

- número y tamaño de capas ocultas;
- dropout;
- regularización L2;
- learning rate;
- batch size;
- ponderación de clases.

El entrenamiento utiliza `EarlyStopping` para recuperar los pesos correspondientes al mejor comportamiento en validación.

El mejor resultado de la partición inicial alcanza:

| Métrica | Resultado |
|---|---:|
| Macro F1 validación | 0,7779 |
| Macro F1 entrenamiento | 0,7327 |
| Balanced Accuracy | 0,7323 |
| Weighted F1 | 0,8681 |

La configuración inicial mejor posicionada utiliza:

```text
hidden_units = [128, 64, 32]
dropout_rate = 0.3
l2_strength = 0.0001
learning_rate = 0.0001
batch_size = 2048
class_weight_mode = none
```

Sin embargo, este resultado no se utiliza directamente para seleccionar la arquitectura definitiva, ya que depende de una única partición temporal.

---

## Validación temporal robusta de GHI

Para comparar MLP y Logistic Regression bajo las mismas condiciones se realiza una validación temporal repetida sobre:

```text
febrero
mayo
agosto
noviembre
```

Cada mes actúa de forma independiente como conjunto de validación y los otros once meses de 2024 se utilizan como entrenamiento.

El preprocesamiento y el escalado se recalculan dentro de cada fold.

Este procedimiento se utiliza como validación temporal por bloques orientada a comprobar la estabilidad estacional de los modelos.

### Validación temporal del MLP

Se evalúan las cinco configuraciones mejor posicionadas en el screening inicial.

La configuración con mejor comportamiento medio obtiene:

| Métrica | Resultado |
|---|---:|
| Macro F1 medio | 0,6411 |
| Desviación estándar Macro F1 | 0,0883 |
| Macro F1 mínimo | 0,5151 |
| Macro F1 medio entrenamiento | 0,7916 |
| Balanced Accuracy media | 0,6043 |
| Weighted F1 medio | 0,9007 |

La arquitectura seleccionada es:

```text
hidden_units = [128, 64]
dropout_rate = 0.5
l2_strength = 0.0001
learning_rate = 0.0001
batch_size = 512
class_weight_mode = none
```

La mediana de la mejor época entre folds es **5,5**, por lo que se establecen **6 épocas** para el entrenamiento definitivo.

### Validación temporal de Logistic Regression

Las cinco mejores configuraciones de Logistic Regression se someten al mismo procedimiento.

La mejor configuración obtiene:

| Métrica | Resultado |
|---|---:|
| Macro F1 medio | 0,5420 |
| Desviación estándar Macro F1 | 0,0731 |
| Macro F1 mínimo | 0,4584 |
| Macro F1 medio entrenamiento | 0,6872 |
| Balanced Accuracy media | 0,5390 |
| Weighted F1 medio | 0,8657 |

La comparación homogénea queda:

| Modelo | Macro F1 medio | Desv. estándar | Macro F1 mínimo | Balanced Accuracy media |
|---|---:|---:|---:|---:|
| MLP | **0,6411** | 0,0883 | **0,5151** | **0,6043** |
| Logistic Regression | 0,5420 | **0,0731** | 0,4584 | 0,5390 |

Aunque Logistic Regression presenta una variabilidad ligeramente menor, el MLP obtiene un rendimiento medio, mínimo y Balanced Accuracy superiores.

Por este motivo se selecciona **MLP como modelo definitivo para GHI**.

---

## Selección final de modelos

La selección definitiva queda establecida como:

| Target | Modelo final | Features |
|---|---|---:|
| `codigo_ghi` | MLP | 14 |
| `codigo_dni` | HistGradientBoostingClassifier | 18 |
| `codigo_dhi` | HistGradientBoostingClassifier | 21 |

Los experimentos de origen son:

```text
codigo_ghi → source_model_id = 22
codigo_dni → source_model_id = 20
codigo_dhi → source_model_id = 3
```

---

## Entrenamiento definitivo

Una vez fijados los algoritmos y sus hiperparámetros, los modelos se entrenan utilizando todos los registros disponibles de 2024.

Los modelos se guardan localmente para evitar repetir el entrenamiento en futuras ejecuciones.

Cuando los archivos ya existen y `FORCE_FINAL_RETRAIN = False`, el notebook carga directamente los modelos persistidos.

Los artefactos son:

```text
../models/final/codigo_ghi_mlp.keras
../models/final/codigo_ghi_scaler.joblib
../models/final/codigo_dni_hgb.joblib
../models/final/codigo_dhi_hgb.joblib
```

---

## Evaluación interanual sobre 2023

Los modelos definitivos se evalúan sobre las **525.600 observaciones de 2023**.

Los resultados se comparan con los obtenidos previamente por los modelos de referencia.

| Target | Modelo | Macro F1 previo | Macro F1 final | Mejora | Balanced Accuracy final | Weighted F1 final |
|---|---|---:|---:|---:|---:|---:|
| GHI | MLP | 0,7435 | **0,8082** | **+0,0647** | 0,7725 | 0,9242 |
| DNI | HistGradientBoostingClassifier | 0,5347 | **0,6448** | **+0,1100** | 0,6350 | 0,9847 |
| DHI | HistGradientBoostingClassifier | 0,4986 | **0,5162** | **+0,0176** | 0,5309 | 0,9026 |

Los tres modelos optimizados mejoran el Macro F1 de referencia.

La mejora más elevada se produce en DNI, seguida de GHI. DHI presenta una mejora más limitada.

La evaluación sobre 2023 debe interpretarse como una **comparación interanual de las configuraciones optimizadas frente a los experimentos anteriores**, ya que los resultados de este año habían sido utilizados previamente durante la comparación inicial de familias de modelos.

---

## Análisis del rendimiento por clase

Las métricas agregadas se complementan con matrices de confusión y gráficos de predicciones correctas e incorrectas por clase.

Los resultados muestran diferencias importantes entre targets:

### GHI

El modelo presenta un buen comportamiento global y clasifica con elevada precisión la clase mayoritaria. El recall de la clase 1 se sitúa aproximadamente en el **57 %**.

### DNI

La clase 1 obtiene un comportamiento considerablemente mejor, con un recall próximo al **83 %**. La clase 2 continúa siendo difícil de detectar y presenta un recall cercano al **8 %**.

### DHI

La clase 1 alcanza un recall aproximado del **62 %**. La clase 2 tiene una frecuencia muy reducida y solo se identifica correctamente en torno al **8 %** de sus registros.

Estas diferencias explican que Weighted F1 alcance valores muy elevados en DNI y DHI mientras Macro F1 se mantiene sensiblemente por debajo.

Las clases minoritarias, especialmente el código 2, constituyen por tanto la principal limitación de los modelos finales.

---

## Persistencia local y reproducibilidad

Además de los modelos, se almacena un archivo de metadata:

```text
../models/final/model_metadata.json
```

Para cada target contiene:

- modelo seleccionado;
- identificador del experimento de origen;
- año de entrenamiento;
- año de evaluación;
- número y listado de features;
- hiperparámetros;
- ruta del modelo;
- ruta del scaler cuando corresponde;
- métricas finales obtenidas sobre 2023.

Los resultados intermedios y finales de optimización se almacenan en:

```text
../outputs/tables/model_optimization/
```

Entre los principales archivos generados se encuentran:

```text
hgb_dni_tuning.parquet
hgb_dhi_tuning.parquet
lr_ghi_tuning.parquet
mlp_ghi_tuning.parquet
mlp_ghi_temporal_cv.parquet
mlp_ghi_temporal_cv_summary.parquet
lr_ghi_temporal_cv.parquet
lr_ghi_temporal_cv_summary.parquet
ghi_model_comparison.parquet
final_model_selection.parquet
final_hyperparameters.json
final_test_results.parquet
final_results_summary.parquet
```

Los resultados de tuning y validación temporal actúan también como checkpoints para evitar repetir procesos costosos cuando el notebook se vuelve a ejecutar.

---

## Persistencia de los modelos finales en PostgreSQL

Los modelos definitivos se registran en PostgreSQL con nombres específicos para diferenciarlos de los experimentos anteriores:

```text
FINAL_OPTIMIZED_MLP_GHI
FINAL_OPTIMIZED_HGB_DNI
FINAL_OPTIMIZED_HGB_DHI
```

Los registros finales quedan asociados a:

| Target | Nombre persistido | PostgreSQL model_id |
|---|---|---:|
| `codigo_ghi` | `FINAL_OPTIMIZED_MLP_GHI` | 25 |
| `codigo_dni` | `FINAL_OPTIMIZED_HGB_DNI` | 26 |
| `codigo_dhi` | `FINAL_OPTIMIZED_HGB_DHI` | 27 |

PostgreSQL almacena la información estructurada de cada modelo:

- target;
- versión del dataset;
- periodo de entrenamiento y evaluación;
- features;
- hiperparámetros;
- métricas globales.

La operación de persistencia evita generar un nuevo registro cuando el mismo modelo final ya existe, manteniendo la trazabilidad en sucesivas ejecuciones.

---

## Persistencia de resultados diarios en MongoDB

Los identificadores de PostgreSQL se utilizan como referencia para incorporar el comportamiento diario de los modelos en MongoDB.

Los resultados se almacenan dentro de los documentos existentes de:

```text
daily_summaries
```

Para cada fecha de 2023 y cada target se incorporan:

- identificador PostgreSQL del modelo;
- nombre del modelo final;
- target;
- métricas de clasificación diarias;
- distribución real de las clases;
- distribución predicha;
- matriz de confusión.

La carga final obtiene:

| Target | Modelo | Días correctos | Días con error |
|---|---|---:|---:|
| `codigo_ghi` | `FINAL_OPTIMIZED_MLP_GHI` | 365 | 0 |
| `codigo_dni` | `FINAL_OPTIMIZED_HGB_DNI` | 365 | 0 |
| `codigo_dhi` | `FINAL_OPTIMIZED_HGB_DHI` | 365 | 0 |

Durante el cálculo diario pueden aparecer avisos cuando una fecha contiene una única clase real o cuando una clase aparece únicamente en las predicciones. Estos casos son consecuencia de la distribución temporal de los códigos y no representan errores de persistencia.

La combinación de ambas bases de datos permite mantener dos niveles complementarios:

- **PostgreSQL:** configuración y rendimiento global del modelo.
- **MongoDB:** comportamiento diario detallado.

Los identificadores PostgreSQL permiten relacionar ambas capas.

---

## Funciones y módulos reutilizados

El notebook reutiliza funciones centralizadas del proyecto para evitar duplicar lógica entre experimentos.

Entre ellas se encuentran funciones para:

- conexión y consulta de PostgreSQL;
- preparación de features;
- construcción y optimización del MLP;
- evaluación de predicciones;
- matrices de confusión;
- persistencia de resultados en PostgreSQL;
- persistencia diaria en MongoDB.

La arquitectura y optimización específica del MLP se encuentra centralizada en:

```text
src/models/mlp.py
```

Las funciones de evaluación se reutilizan desde el módulo común del proyecto.

---

## Ejecución

El notebook debe ejecutarse después de haber completado:

1. El preprocesamiento e imputación del dataset.
2. La carga del dataset `v3` en PostgreSQL.
3. Los experimentos iniciales de modelado y comparación.
4. El almacenamiento en PostgreSQL de las configuraciones y métricas de esos experimentos.
5. La creación previa de los documentos diarios en MongoDB.

La existencia de los archivos de tuning y de los modelos finales permite ejecutar nuevamente el notebook sin repetir automáticamente los entrenamientos más costosos.

Para forzar un nuevo entrenamiento deben activarse explícitamente las variables `FORCE_RETRAIN_*` correspondientes.

---

## Conclusión

La fase de optimización establece una configuración definitiva para cada componente de irradiancia.

El modelo final de GHI es un MLP seleccionado mediante una comparación temporal homogénea frente a Logistic Regression. Para DNI y DHI se seleccionan modelos `HistGradientBoostingClassifier`.

En la comparación interanual sobre 2023, los tres modelos mejoran el Macro F1 de sus configuraciones de referencia:

```text
GHI: 0,7435 → 0,8082
DNI: 0,5347 → 0,6448
DHI: 0,4986 → 0,5162
```

El análisis por clase muestra que las principales limitaciones permanecen asociadas a las clases minoritarias, especialmente el código 2 de DNI y DHI.

Finalmente, los modelos, sus transformaciones, hiperparámetros, metadata y resultados quedan persistidos localmente y en las capas PostgreSQL y MongoDB. De esta forma se completa el ciclo de selección, optimización, evaluación y almacenamiento de los modelos definitivos del proyecto.
