# 04. Imputación de valores nulos

## Objetivo

Este notebook analiza y trata los valores ausentes de las variables meteorológicas y de irradiancia del dataset solar de 2023 y 2024. El objetivo es obtener un conjunto de datos depurado, trazable y adecuado para el posterior entrenamiento de modelos de clasificación orientados a determinar si las mediciones de irradiancia se han registrado correctamente.

La estrategia seguida es conservadora: solo se imputan gaps cortos cuando existe suficiente información temporal en los registros próximos. Los gaps largos se mantienen como valores nulos para evitar introducir estimaciones artificiales con una incertidumbre elevada.

## Dataset de entrada

El notebook utiliza como entrada:

```text
../data/processed/dataset_solar_2023_2024_v2.parquet
```

Las variables analizadas son:

- Irradiancias: `ghi`, `dni` y `dhi`.
- Variables meteorológicas: `temperatura`, `humedad_relativa`, `velocidad_viento`, `direccion_viento_sin` y `direccion_viento_cos`.
- Variable astronómica: `elevacion_solar`.
- Variables objetivo: `codigo_ghi`, `codigo_dni` y `codigo_dhi`.

## Evaluación de fuentes meteorológicas externas

Antes de imputar los valores ausentes, se evalúa la posibilidad de utilizar fuentes meteorológicas externas. Se comparan los datos originales con Open-Meteo y Meteostat mediante patrones mensuales y horarios, así como mediante las métricas MAE y RMSE.

### Open-Meteo

Los datos de Open-Meteo presentan los siguientes errores respecto al dataset original:

| Variable | MAE | RMSE |
|---|---:|---:|
| Temperatura | 1,948 °C | 2,872 °C |
| Humedad relativa | 9,662 puntos porcentuales | 12,194 puntos porcentuales |
| Velocidad del viento | 1,045 m/s | 1,334 m/s |
| Dirección del viento, seno | 0,428 | 0,579 |
| Dirección del viento, coseno | 0,427 | 0,590 |

### Meteostat

Para Meteostat se selecciona la estación Sevilla/Tablada. Los errores obtenidos son:

| Variable | MAE | RMSE |
|---|---:|---:|
| Temperatura | 2,026 °C | 2,920 °C |
| Humedad relativa | 9,976 puntos porcentuales | 12,478 puntos porcentuales |
| Velocidad del viento | 1,299 m/s | 1,746 m/s |
| Dirección del viento, seno | 0,401 | 0,531 |
| Dirección del viento, coseno | 0,433 | 0,568 |

Ambas fuentes reproducen de forma aproximada los patrones generales, pero presentan diferencias relevantes respecto a las mediciones originales. Estas diferencias pueden deberse a la distinta resolución temporal, la localización y altura de los sensores, la instrumentación utilizada y el carácter modelizado de algunos datos.

Por este motivo, ninguna de las dos fuentes se utiliza para sustituir directamente los valores ausentes.

## Identificación de registros meteorológicos anómalos

Durante la exploración se detectan temperaturas extremas y cambios bruscos incompatibles con la evolución meteorológica esperada. Algunos de estos registros coinciden con valores nulos, ceros o anomalías simultáneas en humedad, viento y dirección del viento.

Los registros identificados como fallos de adquisición se transforman en valores nulos antes de aplicar la imputación. La modificación se realiza simultáneamente sobre las variables meteorológicas relacionadas, manteniendo las irradiancias originales sin alteración.

## Análisis de gaps meteorológicos

Tras la depuración se identifican 140 gaps meteorológicos. El mayor tiene una duración aproximada de 376 horas, equivalente a casi 16 días. Los gaps de mayor duración no pueden reconstruirse de forma fiable mediante métodos de interpolación temporal.

La distribución obtenida muestra:

- 120 gaps de hasta 3 horas, equivalentes al 85,71 % del total.
- 119 gaps de hasta 30 minutos, equivalentes al 85,00 % del total.
- Un único gap se encuentra entre 30 minutos y 3 horas.

Aunque la imputación elimina la mayoría de los gaps como unidades independientes, los gaps largos concentran una parte considerable de los registros ausentes y permanecen sin modificar.

## Estrategia de imputación meteorológica

La imputación se realiza de acuerdo con la continuidad y variabilidad de cada variable.

### Temperatura y humedad relativa

Se utiliza interpolación PCHIP para gaps de hasta 3 horas. Este método construye una curva cúbica por tramos y utiliza la tendencia local anterior y posterior al gap. Frente a una interpolación polinómica convencional, PCHIP reduce la aparición de oscilaciones artificiales y preserva mejor la forma de la serie.

### Velocidad del viento

Se utiliza interpolación lineal únicamente para gaps de hasta 30 minutos. El umbral es más restrictivo porque el viento puede presentar cambios rápidos y una menor continuidad temporal que la temperatura y la humedad.

### Dirección del viento

La dirección del viento se trata como una variable circular. No se interpolan de forma independiente sus componentes seno y coseno, ya que esto podría generar combinaciones incompatibles con un ángulo real.

Para gaps de hasta 30 minutos se reconstruye el ángulo anterior y posterior mediante `arctan2`, se calcula la diferencia angular siguiendo el recorrido más corto y, finalmente, se vuelven a obtener las componentes seno y coseno.

## Trazabilidad de la imputación

Se crea la variable binaria:

```text
var_meteo_imp
```

Esta variable permite identificar los registros meteorológicos incluidos dentro de gaps cortos seleccionados para la imputación. Su incorporación conserva información sobre el origen real o estimado de cada observación y facilita el análisis posterior del efecto de la imputación sobre los modelos.

## Resultado de la imputación meteorológica

Después de aplicar los métodos seleccionados permanecen:

- 20 gaps de temperatura y humedad superiores al umbral de imputación.
- 21 gaps asociados a la velocidad del viento superiores a 30 minutos.

El mayor gap conservado sigue siendo de 376,05 horas. Estos periodos se mantienen como nulos porque su reconstrucción temporal no sería suficientemente fiable.

## Tratamiento de los valores ausentes de irradiancia

Se identifican 45 gaps en la variable DNI. El mayor corresponde a un periodo continuo de tres días registrado en marzo de 2024.

Durante la noche, la irradiancia física esperada es aproximadamente cero. Por ello, el análisis se restringe también al periodo diurno, definido mediante:

```text
elevacion_solar > 0
```

Dentro del periodo diurno se identifican 43 gaps, con una duración máxima aproximada de 12,32 horas.

Las irradiancias ausentes no se imputan antes del entrenamiento. Esta decisión se debe a que `ghi`, `dni` y `dhi` son variables esenciales para predecir los códigos de calidad. Su reconstrucción podría eliminar información sobre el fallo original e introducir valores artificiales aparentemente válidos.

Para conservar la información de disponibilidad se crea la variable:

```text
irr_null
```

Esta variable identifica los registros en los que la irradiancia analizada no está disponible y permite diferenciar entre un problema de calidad de una medición existente y un problema de ausencia del dato.

## Dataset de salida

Tras reorganizar las columnas, el dataset procesado se almacena en:

```text
../data/processed/dataset_solar_2023_2024_v3.parquet
```

El resultado conserva:

- las mediciones originales válidas;
- las variables meteorológicas imputadas únicamente en gaps cortos;
- los gaps largos sin reconstruir;
- las irradiancias ausentes sin imputar;
- los indicadores de trazabilidad `var_meteo_imp` e `irr_null`;
- las variables objetivo `codigo_ghi`, `codigo_dni` y `codigo_dhi`.


## Validación final del dataset

El dataset final contiene **1.052.640 registros y 27 variables**, con un tamaño aproximado en memoria de **206,79 MB**. Las variables temporales, la elevación solar, los indicadores de trazabilidad y los códigos objetivo no presentan valores nulos.

Los nulos restantes se concentran en las variables meteorológicas, con aproximadamente un **8,99 %**, y en las irradiancias y variables derivadas de su balance, con un **1,13 %**. Estos valores se conservan deliberadamente porque corresponden a gaps largos o a mediciones de irradiancia ausentes que no deben reconstruirse antes del modelado.

El indicador `irr_null` identifica **11.868 registros** sin irradiancia, equivalentes al **1,13 %** del dataset. Por su parte, `var_meteo_imp` marca **697 registros meteorológicos imputados**, únicamente el **0,066 %** del total, lo que confirma que la estrategia de imputación aplicada ha sido restrictiva.

La mayor parte de las incidencias se concentra en 2024: este año contiene 10.081 registros con irradiancia nula y 687 registros meteorológicos imputados, frente a 1.787 y 10 registros, respectivamente, en 2023. Esta diferencia deberá considerarse al realizar la partición temporal y evaluar los modelos.

## Conclusión

La estrategia aplicada prioriza la trazabilidad y la coherencia física frente a la eliminación completa de los valores nulos. Las fuentes externas se descartan como sustitución directa por sus diferencias respecto al dataset original. Las variables meteorológicas se imputan únicamente en gaps cortos mediante métodos adaptados a su comportamiento temporal, mientras que las irradiancias se conservan sin imputar para no alterar la información necesaria para la clasificación de su calidad.
