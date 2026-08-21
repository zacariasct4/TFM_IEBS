# Notebook 17 — Solución End-to-End y simulación de pseudo-producción

## Objetivo

Integrar los componentes desarrollados durante el proyecto en un flujo reproducible de clasificación automática de la calidad de las mediciones de irradiancia solar.

A diferencia de los notebooks anteriores, este notebook no selecciona ni optimiza nuevos modelos. Se reutilizan las configuraciones finales ya escogidas y se simula su funcionamiento sobre un periodo temporal posterior.

La simulación se plantea de forma retrospectiva:

- **Periodo histórico:** desde el inicio del dataset hasta el 30 de noviembre de 2024.
- **Periodo de pseudo-producción:** diciembre de 2024.
- **Registros históricos:** 1.008.000.
- **Registros de pseudo-producción:** 44.640.

Diciembre no se utiliza en este notebook para modificar modelos, seleccionar variables ni reajustar hiperparámetros.

El flujo general es:

**datos históricos → preparación → reentrenamiento final → inferencia → monitorización → persistencia de resultados**

---

## Modelos finales

Se recuperan del fichero de metadatos los algoritmos, variables e hiperparámetros seleccionados previamente.

| Target | Modelo | Nº de variables |
|---|---|---:|
| `codigo_ghi` | MLP | 14 |
| `codigo_dni` | HistGradientBoostingClassifier | 18 |
| `codigo_dhi` | HistGradientBoostingClassifier | 21 |

Los modelos de DNI y DHI se reentrenan con todo el histórico disponible hasta noviembre de 2024.

Para GHI se reconstruye la MLP optimizada utilizando la configuración final:

- capas ocultas: `[128, 64]`;
- `dropout_rate`: `0.5`;
- regularización L2: `0.0001`;
- `learning_rate`: `0.0001`;
- `batch_size`: `512`;
- `class_weight_mode`: `none`;
- épocas: `6`.

La preparación de variables reutiliza las funciones comunes del proyecto para mantener el mismo tratamiento aplicado durante el desarrollo de los modelos.

---

## Inferencia sobre diciembre de 2024

Los tres modelos generan predicciones para las 44.640 observaciones de diciembre.

Para cada registro se conservan:

- fecha;
- código real;
- código predicho;
- probabilidad de clasificación para `codigo_ghi`.

La disponibilidad posterior de las etiquetas reales permite analizar retrospectivamente cómo habría funcionado la solución durante este periodo de pseudo-producción.

---

## Resultados globales

| Target | F1-macro | Balanced Accuracy | F1-weighted |
|---|---:|---:|---:|
| `codigo_ghi` | 0.641 | 0.608 | 0.832 |
| `codigo_dni` | 0.586 | 0.552 | 0.938 |
| `codigo_dhi` | 0.444 | 0.654 | 0.734 |

El mejor F1-macro durante diciembre corresponde a GHI, seguido de DNI y DHI.

La diferencia entre F1-macro y F1-weighted muestra que existe un fuerte desequilibrio entre clases. Los modelos mantienen un buen comportamiento sobre la clase mayoritaria, pero presentan mayores dificultades para reproducir las clases menos frecuentes.

Estos resultados no se utilizan para reajustar los modelos, sino exclusivamente para monitorizar la configuración final.

---

## Distribución de clases

La distribución real y predicha durante diciembre es:

| Target | Clase | Real (%) | Predicha (%) |
|---|---:|---:|---:|
| `codigo_ghi` | 0 | 83.31 | 96.40 |
| `codigo_ghi` | 1 | 16.69 | 3.60 |
| `codigo_dni` | 0 | 83.68 | 89.36 |
| `codigo_dni` | 1 | 16.23 | 10.64 |
| `codigo_dni` | 2 | 0.09 | 0.00 |
| `codigo_dhi` | 0 | 67.73 | 89.94 |
| `codigo_dhi` | 1 | 32.27 | 10.00 |
| `codigo_dhi` | 2 | 0.00 | 0.06 |

Los tres modelos muestran una tendencia a favorecer la clase mayoritaria.

El efecto es especialmente visible en DHI y ayuda a explicar por qué el F1-weighted resulta significativamente superior al F1-macro.

---

## Comparación con la evaluación anterior

Como referencia, se comparan las métricas obtenidas durante la evaluación previa con las de la simulación de pseudo-producción.

| Target | F1 anterior | F1 pseudo-producción | Balanced Accuracy anterior | Balanced Accuracy pseudo-producción |
|---|---:|---:|---:|---:|
| `codigo_ghi` | 0.808 | 0.641 | 0.772 | 0.608 |
| `codigo_dni` | 0.645 | 0.586 | 0.635 | 0.552 |
| `codigo_dhi` | 0.516 | 0.444 | 0.531 | 0.654 |

El F1-macro disminuye en los tres targets durante diciembre, especialmente en GHI.

Esta comparación es únicamente orientativa, ya que ambos resultados proceden de particiones temporales y esquemas de entrenamiento diferentes. Por tanto, la diferencia no demuestra por sí sola una degradación del modelo, pero sí evidencia que su comportamiento depende del periodo temporal y de la distribución de las clases.

---

## Monitorización diaria

Además de las métricas mensuales, se calcula el rendimiento para cada día de diciembre.

El objetivo es detectar periodos concretos cuyo comportamiento se aleje del patrón habitual, simulando una función básica de monitorización en producción.

En determinados días solo aparece una clase real. En estas situaciones, métricas como F1-macro o balanced accuracy tienen una capacidad discriminativa limitada, lo que explica algunos avisos generados durante la evaluación diaria.

---

## Detección de comportamiento anómalo

El día con peor comportamiento global es el **16 de diciembre de 2024**:

- F1-macro medio de los tres targets: `0.214`;
- errores acumulados: `3.030`.

Resultados individuales:

| Target | F1-macro | Balanced Accuracy | Nº errores |
|---|---:|---:|---:|
| `codigo_ghi` | 0.045 | 0.047 | 1.372 |
| `codigo_dni` | 0.298 | 0.424 | 829 |
| `codigo_dhi` | 0.298 | 0.424 | 829 |

La inspección de las etiquetas revela un comportamiento excepcional:

| Target | Clase real | Registros | Porcentaje |
|---|---:|---:|---:|
| `codigo_ghi` | 1 | 1.440 | 100 % |
| `codigo_dni` | 1 | 1.440 | 100 % |
| `codigo_dhi` | 1 | 1.440 | 100 % |

Las 1.440 observaciones del día pertenecen a la clase `1` para los tres targets.

Además, se observan registros nocturnos con `GHI = DNI = DHI = 0` etiquetados como clase `1`, mientras que el modelo de GHI los clasifica como `0`.

Por tanto, el deterioro de ese día no debe atribuirse exclusivamente a una pérdida general de capacidad predictiva. El pipeline permite detectar un cambio excepcional en el patrón de etiquetas que, en un entorno real, debería activar una revisión de la calidad de los datos, del proceso de etiquetado o de las condiciones específicas de esa jornada.

---

## Persistencia de resultados

La simulación genera los siguientes archivos:

- `predictions_december_2024.parquet`: predicciones minuto a minuto;
- `monthly_metrics.csv`: métricas globales del periodo;
- `daily_metrics.csv`: métricas diarias de monitorización;
- `metrics_comparison.csv`: comparación orientativa con la evaluación anterior.

Los resultados se almacenan en:

```text
outputs/end_to_end/
```

Esto permite desacoplar la inferencia de procesos posteriores de análisis, visualización o almacenamiento.

---

## Conclusiones

La simulación End-to-End demuestra que los modelos seleccionados pueden integrarse en un flujo único que incluye:

1. preparación de datos;
2. reconstrucción y reentrenamiento de los modelos finales;
3. inferencia sobre un periodo temporal posterior;
4. evaluación y monitorización temporal;
5. detección de comportamientos anómalos;
6. persistencia de resultados.

La principal aportación del notebook no consiste en mejorar nuevamente los algoritmos, sino en demostrar cómo los componentes desarrollados durante el proyecto pueden utilizarse conjuntamente como una **solución reproducible de clasificación y monitorización de la calidad de las mediciones de irradiancia**.

La monitorización diaria muestra además que las métricas agregadas pueden ocultar cambios relevantes en los datos. El caso del 16 de diciembre ejemplifica cómo el propio pipeline puede servir para identificar situaciones que requieren revisión.

Como limitación, esta prueba constituye una simulación retrospectiva sobre datos disponibles durante el desarrollo global del proyecto y no una validación prospectiva sobre nuevas mediciones adquiridas después de finalizar los modelos. Como trabajo futuro, nuevos datos permitirían evaluar con mayor rigor la estabilidad temporal de la solución y detectar posibles fenómenos de *data drift* o *concept drift*.
