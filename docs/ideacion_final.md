# Ideación final del Global Project

## 1. Problema abordado

Las mediciones de irradiancia solar minuto a minuto pueden contener valores nulos, incoherencias físicas, anomalías y códigos de calidad desbalanceados entre clases. Esta situación afecta a la fiabilidad de análisis posteriores, a la evaluación del recurso solar y a la explotación de los datos en sistemas de monitorización y toma de decisiones.

El proyecto aborda este problema mediante una solución de **Data Science, Machine Learning y Big Data** orientada a clasificar automáticamente los códigos de calidad de las tres componentes principales de irradiancia:

- `codigo_ghi`;
- `codigo_dni`;
- `codigo_dhi`.

El problema se formula como **clasificación supervisada multiclase**, complementada con reglas físicas, análisis temporal, control de calidad del dato e interpretabilidad.

---

## 2. Contexto y datos

El trabajo utiliza mediciones solares correspondientes a **2023 y 2024 en Sevilla**, con frecuencia aproximada de un minuto.

Tras las fases de preparación e imputación, el dataset principal del proyecto es:

```text
data/processed/dataset_solar_2023_2024_v3.parquet
```

con:

- **1.052.640 registros**;
- **27 variables**.

La información utilizada combina:

- GHI, DNI y DHI;
- GHI estimado;
- variables temporales;
- elevación y periodo solar;
- temperatura, humedad y viento;
- variables de balance físico;
- indicadores de nulos e imputación;
- códigos de calidad objetivo.

---

## 3. Motivación de la solución

El control de calidad manual o basado únicamente en reglas rígidas puede resultar insuficiente cuando se trabaja con grandes volúmenes de datos minuto a minuto y con patrones que dependen simultáneamente de condiciones solares, meteorológicas y temporales.

La solución propuesta combina:

1. conocimiento físico del problema;
2. preparación y estructuración reproducible de los datos;
3. almacenamiento relacional y documental;
4. modelos de clasificación supervisada;
5. evaluación con métricas adecuadas para clases desbalanceadas;
6. interpretabilidad;
7. una simulación final end-to-end.

El objetivo no es sustituir completamente los criterios físicos de validación, sino complementarlos con modelos capaces de aprender patrones presentes en los datos históricos.

---

## 4. Objetivo general final

**Desarrollar y validar una solución end-to-end de Data Science, Machine Learning y Big Data para clasificar automáticamente la calidad de mediciones minuto a minuto de GHI, DNI y DHI, integrando preparación de datos, almacenamiento, modelado, evaluación, interpretabilidad y una simulación retrospectiva de inferencia.**

---

## 5. Objetivos específicos finales

### Objetivo específico 1

**Construir un dataset analítico reproducible y físicamente coherente** a partir de los datos históricos de 2023 y 2024, incorporando limpieza, feature engineering, análisis exploratorio y tratamiento controlado de valores ausentes.

### Objetivo específico 2

**Diseñar una arquitectura de almacenamiento y procesamiento** que combine PostgreSQL para datos estructurados y trazabilidad, MongoDB para resúmenes documentales diarios, Parquet como formato analítico y Spark como demostración de procesamiento distribuido.

### Objetivo específico 3

**Comparar, seleccionar y optimizar modelos de clasificación supervisada** para `codigo_ghi`, `codigo_dni` y `codigo_dhi`, utilizando una estrategia temporal y métricas robustas frente al desequilibrio de clases.

### Objetivo específico 4

**Evaluar la interpretabilidad, los errores y la aplicabilidad end-to-end de la solución**, integrando los modelos finales en una simulación de pseudo-producción sobre un periodo temporal posterior y generando resultados reutilizables para monitorización.

---

## 6. Solución desarrollada

La solución final se estructura en las siguientes fases.

### Fase 1. Inventario y preparación de datos

Se analizan las fuentes originales, se homogeneizan columnas, tipos y fechas, y se construye una estructura reproducible de procesamiento.

### Fase 2. Feature engineering y análisis exploratorio

Se incorporan variables temporales cíclicas, variables de geometría solar y errores de balance entre componentes de irradiancia. Se estudian distribuciones, correlaciones, diferencias temporales, valores extremos y patrones de calidad.

### Fase 3. Tratamiento de valores ausentes

Se analizan los patrones de missing data y se aplican estrategias de imputación controladas según la naturaleza y duración de los huecos. El proceso genera el dataset `v3`, utilizado como base del resto del proyecto.

### Fase 4. Persistencia relacional con PostgreSQL

Se almacenan las mediciones procesadas, versiones del dataset, vistas, modelos y métricas. La base de datos permite mantener trazabilidad entre datos y experimentos.

### Fase 5. Persistencia documental con MongoDB

Cada día se transforma en un documento agregado con estadísticas, indicadores de calidad y referencias a gráficas. La carga final contiene **731 documentos diarios**, uno por cada fecha entre 2023 y 2024, sin errores de carga.

### Fase 6. Preparación del modelado

Se definen los targets, se excluyen variables no adecuadas para la predicción y se prepara una metodología temporal para evitar mezclar de forma aleatoria observaciones consecutivas.

### Fase 7. Comparación de modelos clásicos

Se comparan diferentes algoritmos de clasificación supervisada para cada target, utilizando **Macro F1** como métrica principal y Balanced Accuracy y Weighted F1 como métricas complementarias.

### Fase 8. Spark y Deep Learning

Se utiliza PySpark para cargar, transformar y particionar el dataset, y TensorFlow/Keras para entrenar redes neuronales MLP. Esta fase amplía el proyecto hacia procesamiento distribuido y Deep Learning.

### Fase 9. Selección y optimización final

Se recuperan los mejores candidatos y se optimizan sus hiperparámetros. Los modelos finales son:

| Target | Modelo final | Nº features |
|---|---|---:|
| `codigo_ghi` | MLP | 14 |
| `codigo_dni` | HistGradientBoostingClassifier | 18 |
| `codigo_dhi` | HistGradientBoostingClassifier | 21 |

Las métricas de referencia almacenadas para la evaluación 2023 son:

| Target | F1 macro | Balanced Accuracy | F1 weighted |
|---|---:|---:|---:|
| `codigo_ghi` | 0.808 | 0.772 | 0.924 |
| `codigo_dni` | 0.645 | 0.635 | 0.985 |
| `codigo_dhi` | 0.516 | 0.531 | 0.903 |

### Fase 10. Interpretabilidad y análisis de errores

Se utilizan Permutation Importance y SHAP para estudiar la dependencia de los modelos respecto a las variables y comprender cómo contribuyen las features a las predicciones.

Se analizan además los errores según condiciones solares, temporales y de calidad del dato.

### Fase 11. Solución end-to-end

Se simula una puesta en producción retrospectiva utilizando diciembre de 2024 como periodo de pseudo-producción.

El escenario utiliza:

- **1.008.000 registros históricos** anteriores al 1 de diciembre de 2024;
- **44.640 observaciones** correspondientes a diciembre de 2024.

Las configuraciones de los modelos se mantienen congeladas y se reentrenan únicamente con la información disponible hasta noviembre.

Las métricas de pseudo-producción son:

| Target | F1 macro | Balanced Accuracy |
|---|---:|---:|
| `codigo_ghi` | 0.641 | 0.608 |
| `codigo_dni` | 0.586 | 0.552 |
| `codigo_dhi` | 0.444 | 0.654 |

Esta prueba demuestra la integración técnica del pipeline y permite analizar la estabilidad temporal de los modelos.

---

## 7. Arquitectura tecnológica final

La arquitectura utiliza tecnologías con funciones diferenciadas:

| Tecnología | Papel en el proyecto |
|---|---|
| Python | ETL, análisis, modelado y orquestación |
| Pandas / NumPy | Tratamiento analítico local |
| Parquet | Almacenamiento eficiente de datasets analíticos |
| PostgreSQL | Datos estructurados, versionado y resultados de modelos |
| MongoDB Atlas | Resúmenes diarios y metadatos documentales |
| Scikit-learn | Modelos clásicos y evaluación |
| TensorFlow / Keras | Redes neuronales MLP |
| Spark / PySpark | Procesamiento distribuido |
| SHAP | Interpretabilidad de modelos |
| Matplotlib | Visualización |
| Git / GitHub | Versionado y reproducibilidad |

---

## 8. Valor aportado

El valor del proyecto no reside únicamente en obtener un clasificador para cada componente de irradiancia.

La aportación global consiste en integrar en un mismo trabajo:

- datos solares reales de alta frecuencia;
- conocimiento físico del dominio;
- ETL y feature engineering;
- almacenamiento SQL y NoSQL;
- trazabilidad de experimentos;
- Machine Learning clásico;
- Deep Learning;
- procesamiento distribuido;
- interpretabilidad;
- monitorización temporal;
- una demostración end-to-end.

Esto permite plantear la solución como base para un sistema de apoyo al **control automático de calidad de estaciones de medida de radiación solar**.

---

## 9. Aplicabilidad

En un escenario real, la arquitectura podría evolucionar hacia un flujo en el que nuevas mediciones fueran procesadas automáticamente para:

1. validar el esquema y la calidad básica de entrada;
2. generar las variables derivadas;
3. aplicar los modelos correspondientes a GHI, DNI y DHI;
4. producir códigos de calidad;
5. registrar resultados;
6. monitorizar el comportamiento temporal;
7. generar alertas o indicadores para supervisión técnica.

La simulación de diciembre de 2024 constituye una demostración retrospectiva de este flujo, no un despliegue productivo real.

---

## 10. Limitaciones identificadas

Los resultados finales evidencian varias limitaciones relevantes:

- fuerte desequilibrio entre clases;
- peor capacidad predictiva sobre las clases minoritarias;
- sensibilidad del rendimiento al periodo temporal;
- menor F1 macro en pseudo-producción que en la evaluación anterior;
- ausencia de nuevos datos externos posteriores a 2024 para realizar una validación prospectiva real.

Estas limitaciones no invalidan la solución, pero condicionan su interpretación y delimitan los pasos necesarios antes de un despliegue real.

---

## 11. Evolución respecto a la ideación inicial

La idea inicial contemplaba algunos elementos como opcionales o provisionales. Durante el desarrollo se consolidaron como partes reales del proyecto:

- MongoDB pasó de componente opcional a capa documental completa con 731 resúmenes diarios;
- Spark se integró efectivamente en el pipeline;
- el problema quedó definido como clasificación de `codigo_ghi`, `codigo_dni` y `codigo_dhi`, en lugar de una clasificación genérica correcto/incorrecto;
- se incorporó Deep Learning mediante MLP;
- se añadió interpretabilidad mediante Permutation Importance y SHAP;
- se desarrolló una fase final end-to-end con pseudo-producción;
- los objetivos dejaron de ser provisionales y quedaron vinculados a resultados concretos.

Por este motivo, `ideacion_v0.md` se conserva únicamente como registro de la fase inicial de definición del proyecto, mientras este documento recoge la formulación final realmente desarrollada.