# 12 - Preparación del modelado y modelos de referencia

## Objetivo

Este notebook inicia la fase de modelado del proyecto a partir del dataset procesado `dataset_solar_2023_2024_v3.parquet`.

Los objetivos principales son:

- definir las variables objetivo y las variables predictoras;
- revisar el desbalance de los códigos de calidad;
- establecer una estrategia de validación interanual;
- definir las métricas comunes de evaluación;
- construir un modelo trivial de referencia y un primer modelo supervisado;
- estandarizar el procedimiento de evaluación para los modelos posteriores;
- registrar los experimentos globales en PostgreSQL;
- almacenar el comportamiento diario de los modelos en MongoDB.

---

## Datos de entrada

**Dataset utilizado**

```text
../data/processed/dataset_solar_2023_2024_v3.parquet
```

El dataset contiene **1.052.640 registros** correspondientes a los años 2023 y 2024, con resolución temporal de un minuto.

Las variables objetivo son:

- `codigo_ghi`
- `codigo_dni`
- `codigo_dhi`

---

## Distribución de las variables objetivo

Se realiza una revisión resumida de la distribución de los códigos de calidad, cuyo análisis detallado ya había sido desarrollado durante el EDA.

Las tres variables presentan un claro desbalance:

- `codigo_ghi` es un problema binario.
- `codigo_dni` y `codigo_dhi` son problemas multiclase con una tercera clase muy minoritaria.
- La clase 0 representa aproximadamente entre el 81,7 % y el 89,6 % de los registros.
- La clase 2 representa aproximadamente el 0,18 % de los registros en DNI y el 0,04 % en DHI.

También se compara la distribución entre años. La clase 1 tiene una representación sensiblemente mayor en 2024:

| Target | 2023 | 2024 |
|---|---:|---:|
| GHI - clase 1 | 11,92 % | 17,08 % |
| DNI - clase 1 | 3,95 % | 16,37 % |
| DHI - clase 1 | 10,93 % | 25,57 % |

Estas diferencias se tienen en cuenta al definir la estrategia de entrenamiento y evaluación.

---

## Variables predictoras

Se excluyen de las variables candidatas:

- las tres variables objetivo;
- `fecha`, por actuar como identificador temporal;
- `ano`, porque queda constante dentro de cada partición interanual y no aporta capacidad predictiva.

El conjunto final utilizado por los modelos contiene **22 variables predictoras**.

Las variables binarias se transforman a formato numérico:

- `periodo_solar`: `noche = 0`, `dia = 1`;
- `var_meteo_imp`: conversión a entero;
- `irr_null`: conversión a entero.

La revisión previa muestra que las variables temporales y solares se encuentran prácticamente completas, mientras que permanecen algunos valores ausentes en irradiancias, magnitudes derivadas y variables meteorológicas.

No se introducen nuevas imputaciones en esta fase. Se priorizan inicialmente algoritmos capaces de trabajar con valores ausentes de forma nativa.

---

## Estrategia de entrenamiento y evaluación

Se utiliza una **validación interanual**:

```text
Entrenamiento: 2024
Prueba:        2023
```

Tamaños obtenidos:

```text
Train 2024: 527.040 registros
Test 2023:  525.600 registros
```

La elección de 2024 como conjunto de entrenamiento responde principalmente a su mayor representación de las clases minoritarias.

La separación completa entre años evita además mezclar observaciones temporalmente muy próximas entre entrenamiento y prueba, algo especialmente relevante en un dataset minuto a minuto.

Esta estrategia debe interpretarse como una evaluación de la capacidad de generalización entre años y no como una predicción cronológica de un periodo futuro.

---

## Métricas de evaluación

Debido al fuerte desbalance de clases, la exactitud global no se utiliza como métrica principal.

### Métrica principal

**Macro F1**

Calcula el F1 de cada clase de forma independiente y posteriormente obtiene la media sin ponderar por frecuencia. De esta forma, las clases minoritarias tienen el mismo peso que las mayoritarias.

### Métricas complementarias

**Balanced Accuracy**

Permite evaluar la capacidad del modelo para identificar correctamente las distintas clases sin quedar dominada por la clase mayoritaria.

**Weighted F1**

Pondera el F1 de cada clase según su frecuencia y proporciona una visión global del rendimiento.

### Análisis adicional

Se utilizan matrices de confusión para estudiar la distribución de los errores y el comportamiento de los modelos sobre cada clase.

---

## Modelo de referencia: DummyClassifier

Como referencia mínima se utiliza:

```python
DummyClassifier(strategy="most_frequent")
```

El modelo predice sistemáticamente la clase mayoritaria y no utiliza información de las variables predictoras.

Por este motivo se registra con:

```text
n_features = 0
features = []
```

### Resultados

| Target | Macro F1 | Balanced Accuracy | Weighted F1 |
|---|---:|---:|---:|
| `codigo_ghi` | 0,468 | 0,500 | 0,825 |
| `codigo_dni` | 0,326 | 0,333 | 0,938 |
| `codigo_dhi` | 0,314 | 0,333 | 0,839 |

Los valores elevados de Weighted F1 muestran cómo el fuerte desbalance puede generar una impresión engañosa de buen rendimiento incluso en un modelo sin capacidad predictiva real.

Esto refuerza el uso de Macro F1 como métrica principal.

---

## Primer modelo supervisado: HistGradientBoostingClassifier

Se utiliza `HistGradientBoostingClassifier` como primera referencia supervisada debido, entre otros motivos, a su capacidad para trabajar de forma nativa con valores ausentes.

Configuración inicial:

```python
HistGradientBoostingClassifier(
    random_state=42
)
```

En esta fase no se realiza todavía optimización de hiperparámetros.

### Resultados

| Target | Macro F1 | Balanced Accuracy | Weighted F1 |
|---|---:|---:|---:|
| `codigo_ghi` | 0,626 | 0,613 | 0,851 |
| `codigo_dni` | 0,487 | 0,617 | 0,932 |
| `codigo_dhi` | 0,499 | 0,573 | 0,882 |

El modelo supera al `DummyClassifier` en los tres objetivos.

Mejora absoluta aproximada de Macro F1:

```text
GHI: +0,158
DNI: +0,161
DHI: +0,185
```

Aunque la mejora es clara, la diferencia entre Macro F1 y Weighted F1 sigue mostrando que las clases minoritarias continúan siendo las más difíciles de clasificar.

---

## Funciones reutilizables de evaluación

Para evitar duplicar lógica en los siguientes notebooks se utilizan funciones comunes definidas en:

```text
src/evaluation/evaluation.py
```

Funciones principales:

```python
evaluate_model_predictions()
plot_confusion_matrices()
plot_correct_predictions_by_class()
create_model_comparison_table()
```

Estas funciones permiten:

- calcular de forma homogénea las métricas de cada modelo;
- representar matrices de confusión;
- analizar aciertos y errores por clase;
- mantener una tabla comparativa común entre experimentos.

El procedimiento se valida reproduciendo los resultados obtenidos previamente con `HistGradientBoostingClassifier`.

A partir de este punto, los modelos posteriores deberán evaluarse mediante este mismo flujo.

---

## Persistencia en PostgreSQL

PostgreSQL se utiliza para almacenar los resultados globales y estructurados de los experimentos.

Para cada combinación modelo-target se registra:

- versión del dataset;
- nombre del modelo;
- target;
- año de entrenamiento;
- año de prueba;
- número de features;
- listado de features;
- hiperparámetros;
- Macro F1;
- Balanced Accuracy;
- Weighted F1.

Los resultados quedan relacionados con la versión:

```text
processed_dataset_solar_v3
```

El `DummyClassifier` se registra con cero variables predictoras, mientras que `HistGradientBoostingClassifier` utiliza las 22 features definidas.

Las llamadas de inserción quedan comentadas en el notebook una vez realizado el registro para evitar generar duplicados al volver a ejecutar el notebook.

Los identificadores almacenados se reutilizan posteriormente para mantener la trazabilidad con MongoDB.

---

## Persistencia diaria en MongoDB

MongoDB complementa la información global de PostgreSQL almacenando el rendimiento diario de los modelos dentro de los documentos existentes de:

```text
daily_summaries
```

Los resultados se incorporan en:

```text
resultados_modelos.ejecuciones
```

Para cada modelo y target se almacenan, entre otros elementos:

- `postgresql_model_id`;
- nombre del modelo;
- target;
- versión del dataset;
- años de entrenamiento y prueba;
- número de features;
- métricas diarias;
- clases;
- distribución real;
- distribución predicha;
- matriz de confusión.

La persistencia es idempotente: una nueva ejecución de la misma combinación modelo-target actualiza la información existente y no crea duplicados.

Se registran diariamente:

- `HistGradientBoostingClassifier`;
- `DummyClassifier`.

Por tanto, cada documento de 2023 contiene **6 ejecuciones**:

```text
2 modelos × 3 targets = 6 ejecuciones
```

---

## Validación de MongoDB

La carga masiva se valida sobre los 365 días del conjunto de prueba.

Resultados:

```text
Días 2023 con resultados: 365

HistGradientBoosting:
- días correctos: 365
- días con error: 0

DummyClassifier:
- días correctos: 365
- días con error: 0

Documentos con número incorrecto de ejecuciones: 0
```

La validación confirma la cobertura completa del periodo y la ausencia de duplicados en los documentos diarios.

---

## Resultados principales

El notebook deja definido un flujo común para la fase de modelado:

```text
Dataset procesado
        ↓
Selección de features y targets
        ↓
Validación interanual
        ↓
Entrenamiento
        ↓
Predicciones
        ↓
Evaluación común
        ↓
Comparación de modelos
        ↓
PostgreSQL: resultados globales
        ↓
MongoDB: comportamiento diario
```

El `DummyClassifier` establece el nivel mínimo de referencia y el `HistGradientBoostingClassifier` demuestra que existe señal predictiva suficiente para mejorar claramente ese baseline en los tres códigos de calidad.

---

## Conclusiones

Este notebook establece la metodología que se reutilizará durante el resto de la fase de modelado.

Las decisiones principales son:

- utilizar 2024 como conjunto de entrenamiento y 2023 como conjunto independiente de prueba;
- emplear Macro F1 como criterio principal de comparación;
- complementar la evaluación con Balanced Accuracy, Weighted F1 y matrices de confusión;
- mantener un `DummyClassifier` como baseline trivial;
- utilizar `HistGradientBoostingClassifier` como primera referencia supervisada;
- centralizar las funciones de evaluación;
- registrar los resultados globales en PostgreSQL;
- almacenar el comportamiento diario en MongoDB.

Los siguientes modelos podrán incorporarse al mismo procedimiento de entrenamiento, evaluación, comparación y persistencia sin modificar la arquitectura general del proyecto.
