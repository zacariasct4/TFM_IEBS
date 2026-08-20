# 16. Interpretabilidad y análisis de errores de los modelos finales

## Objetivo

Este notebook complementa la evaluación predictiva realizada previamente sobre los modelos finales de **GHI, DNI y DHI**. El objetivo ya no es comparar ni optimizar modelos, sino comprender:

- qué variables sostienen su rendimiento;
- cómo contribuyen las variables a las predicciones;
- por qué se producen determinadas decisiones individuales;
- en qué condiciones solares, temporales o de calidad de datos se concentran los errores.

---

## Preparación del análisis

Se cargan:

- el dataset procesado `dataset_solar_2023_2024_v3.parquet`;
- los modelos finales seleccionados en el notebook anterior;
- el `scaler` asociado al modelo MLP de GHI;
- los metadatos de los modelos, utilizados para recuperar las features y el año de evaluación.

Las variables predictoras se preparan reutilizando la función `convert_model_dtypes` definida en `src`, garantizando el mismo tratamiento aplicado durante el modelado.

---

## 1. Permutation Importance

Se utiliza **Permutation Importance** para estudiar qué variables son necesarias para mantener el rendimiento de cada modelo.

La técnica permuta aleatoriamente una variable y cuantifica la pérdida de **F1-macro**. Cuanto mayor sea la caída de rendimiento, mayor es la dependencia predictiva del modelo respecto a dicha característica.

El análisis se realiza sobre una muestra de **20.000 observaciones** del conjunto de evaluación.

### Principales resultados

- **GHI:** `error_balance_abs` es la variable claramente dominante. También destacan `hora_cos`, `elevacion_solar` y variables asociadas a las propias componentes de irradiancia.
- **DNI:** `velocidad_viento` presenta una importancia muy superior al resto, seguida por `dni`, `hora_sin` y `elevacion_solar`.
- **DHI:** la importancia está más distribuida entre `dhi`, `error_balance`, `velocidad_viento` y `temperatura`.

Los tres modelos utilizan, por tanto, combinaciones diferentes de información radiométrica, meteorológica, solar y temporal.

Estas importancias representan **dependencia predictiva** y no relaciones causales.

---

## 2. Interpretabilidad global mediante SHAP

Se emplea **SHAP** para complementar Permutation Importance y estudiar cómo contribuyen las variables a las predicciones.

Debido a su mayor coste computacional, se utiliza una muestra estratificada de **200 observaciones por modelo**, garantizando representación de los diferentes códigos de calidad.

Para GHI se utiliza `GradientExplainer`, adaptado al modelo neuronal, mientras que los modelos de DNI y DHI se interpretan mediante sus respectivos explainers.

### Principales resultados

#### GHI

SHAP destaca principalmente variables temporales y solares, entre ellas:

- `mes_cos`;
- `dia`;
- `hora_cos`;
- `mes_sin`;
- `elevacion_solar`.

La coincidencia entre las cinco variables principales de SHAP y Permutation Importance es del **40 %**. Esto indica que ambas técnicas muestran perspectivas complementarias: Permutation Importance destaca especialmente el balance radiométrico, mientras SHAP refleja una influencia importante de la estructura temporal y solar en las predicciones individuales.

#### DNI

Existe una elevada consistencia entre ambos métodos. `velocidad_viento` vuelve a ocupar una posición dominante y aparecen también `mes_sin`, `elevacion_solar`, `dni` y `hora_sin`.

La coincidencia Top-5 entre SHAP y Permutation Importance alcanza el **100 %**.

#### DHI

SHAP destaca principalmente:

- `temperatura`;
- `error_balance_rel`;
- `error_balance`;
- `dhi`.

La coincidencia Top-5 con Permutation Importance es del **60 %**, mostrando una consistencia intermedia.

---

## 3. Interpretabilidad local

Se utiliza SHAP local para estudiar **por qué se produce una predicción concreta**.

Para cada target se seleccionan:

- una clasificación correcta de elevada confianza;
- una clasificación incorrecta también realizada con elevada confianza.

Los gráficos *waterfall* muestran cómo cada variable desplaza la salida desde el valor de referencia hasta la predicción final.

### Principales resultados

Se observan errores realizados con confianzas elevadas:

- **GHI:** aproximadamente **93,4 %**;
- **DNI:** aproximadamente **96,8 %**;
- **DHI:** aparece un error con confianza prácticamente máxima.

Estos casos muestran que una elevada confianza no garantiza necesariamente una clasificación correcta. El análisis no constituye una evaluación formal de calibración, pero permite identificar qué combinación de variables impulsa decisiones individuales especialmente relevantes o inesperadas.

---

## 4. Análisis de errores

Se estudia sobre el conjunto completo de evaluación en qué condiciones se concentran los fallos.

Se consideran dos grupos principales:

1. **Condiciones solares y temporales**
   - periodo solar;
   - elevación solar;
   - hora del día.

2. **Calidad y tratamiento de datos**
   - `irr_null`;
   - `var_meteo_imp`.

### Condiciones solares y temporales

#### GHI

La tasa global de error es relativamente similar entre día y noche, pero aumenta considerablemente cuando la elevación solar se encuentra entre **0° y 5°**, alcanzando aproximadamente el **19,7 %**.

La mayor tasa horaria aparece alrededor de las **05:00**, indicando que las transiciones próximas al amanecer constituyen una región especialmente compleja.

#### DNI

El comportamiento general es más estable y las tasas de error son menores. No obstante, el intervalo entre **0° y 5°** de elevación solar también presenta un incremento, con aproximadamente **6,9 %** de error.

#### DHI

El comportamiento es diferente:

- error diurno aproximado: **21,5 %**;
- error nocturno aproximado: **4,5 %**;
- entre **60° y 90°** de elevación solar, la tasa de error alcanza aproximadamente el **44,6 %**.

Por tanto, GHI y DNI presentan mayores dificultades cerca del horizonte, mientras que DHI concentra una elevada proporción de errores durante condiciones diurnas y con elevaciones solares altas.

### Influencia de la calidad de los datos

El resultado más relevante aparece en GHI.

Los **1.787 registros** con `irr_null = True` son clasificados incorrectamente, lo que representa una tasa de error del **100 %** dentro de este subconjunto.

Esto identifica una limitación concreta que podría requerir un tratamiento específico en una futura aplicación del sistema.

Los registros con `var_meteo_imp = True` también presentan tasas de error elevadas, pero únicamente existen **10 observaciones** de este tipo en el conjunto de evaluación. El tamaño muestral es demasiado reducido para obtener conclusiones generalizables.

---

## 5. Síntesis de interpretabilidad y errores

Los distintos análisis responden a preguntas complementarias:

- **Permutation Importance:** qué variables son necesarias para mantener el rendimiento.
- **SHAP global:** cómo se distribuye la contribución de las variables entre las predicciones.
- **SHAP local:** por qué se produce una decisión individual.
- **Análisis de errores:** bajo qué condiciones los modelos presentan mayores dificultades.

La coincidencia entre las cinco principales variables identificadas mediante Permutation Importance y SHAP es:

| Target | Coincidencia Top-5 |
|---|---:|
| GHI | 40 % |
| DNI | 100 % |
| DHI | 60 % |

DNI presenta la interpretación más estable entre técnicas, DHI una concordancia parcial y GHI una mayor complementariedad entre ambos enfoques.

---

## Conclusiones

Los modelos finales de GHI, DNI y DHI utilizan la información disponible de manera diferente y presentan también patrones de error distintos.

En **GHI**, Permutation Importance muestra una fuerte dependencia del balance radiométrico, mientras SHAP destaca también variables temporales y solares. En **DNI**, ambos métodos presentan una elevada concordancia y sitúan a `velocidad_viento` como una de las variables más relevantes. En **DHI**, la importancia se reparte entre variables meteorológicas, radiométricas y relacionadas con el balance.

El análisis local evidencia además que pueden producirse errores con niveles elevados de confianza, lo que refuerza la utilidad de disponer de técnicas de explicabilidad para estudiar predicciones individuales.

Finalmente, el análisis de errores identifica regiones específicas de menor fiabilidad:

- GHI y DNI presentan mayores dificultades con elevaciones solares próximas al horizonte;
- DHI concentra una proporción elevada de errores durante el día y con elevaciones solares altas;
- los registros con irradiancia ausente constituyen una limitación especialmente importante para GHI.

En conjunto, el notebook permite pasar de conocer únicamente **cuánto aciertan los modelos** a comprender también **qué información utilizan, cómo construyen determinadas decisiones y bajo qué condiciones presentan sus principales limitaciones**.
