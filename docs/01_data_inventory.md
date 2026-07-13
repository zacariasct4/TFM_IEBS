# Documentación del notebook `01_data_inventory.ipynb`

## 1. Propósito

Este notebook realiza el inventario y la evaluación exploratoria inicial de los datos brutos del proyecto de clasificación de la calidad de mediciones de irradiancia solar.

Su finalidad es conocer la estructura, cobertura temporal, calidad básica y consistencia de los ficheros disponibles antes de aplicar transformaciones. El notebook no modifica los datos originales: únicamente los carga, inspecciona y genera un inventario tabular.

## 2. Alcance

El análisis comprende:

- localización automática de ficheros Excel en `data/raw`;
- creación de un inventario de archivos;
- revisión de estructura, dimensiones y tipos de datos;
- identificación de valores ausentes;
- comprobación de duplicados y orden temporal;
- análisis descriptivo inicial de variables físicas y meteorológicas;
- inspección de los códigos de calidad;
- revisión del fichero de elevación solar de 2023;
- identificación preliminar de valores potencialmente anómalos.

## 3. Entradas

El notebook busca todos los archivos `.xlsx` y `.xls` dentro de:

```text
data/raw/
```

En la ejecución documentada se identificaron tres ficheros:

| Fichero | Filas | Columnas | Descripción |
|---|---:|---:|---|
| `datos_2023.xlsx` | 525.600 | 16 | Mediciones de irradiancia, meteorología y códigos de calidad de 2023 |
| `datos_2024.xlsx` | 527.040 | 15 | Mediciones equivalentes de 2024, sin columna de año |
| `altura_min_sevilla.xlsx` | 525.601 | 7 | Elevación solar por minuto para 2023, más un registro adicional |

Los nombres concretos pueden variar si se reorganiza la carpeta `data/raw`, ya que la primera parte del notebook realiza una búsqueda recursiva.

## 4. Dependencias

```python
pandas
pathlib
```

No se requieren librerías de modelado ni conexión a bases de datos.

## 5. Flujo de trabajo

### 5.1. Localización de archivos

Se utiliza `Path.rglob()` para buscar recursivamente todos los ficheros Excel:

```python
RAW_PATH = Path("../data/raw")

excel_files = (
    list(RAW_PATH.rglob("*.xlsx"))
    + list(RAW_PATH.rglob("*.xls"))
)
```

Esto permite que el inventario siga funcionando aunque los archivos se organicen en subcarpetas dentro de `data/raw`.

### 5.2. Creación del inventario

Para cada fichero se registran:

- nombre;
- ruta;
- carpeta;
- número de filas;
- número de columnas;
- nombres de las columnas;
- número total de valores ausentes;
- porcentaje global de valores ausentes;
- error de lectura, si se produce.

El inventario se convierte en un `DataFrame` y se exporta a:

```text
reports/tables/data_inventory.csv
```

### 5.3. Carga de los datasets anuales

Se cargan los datos de 2023 y 2024 para comparar:

- cabeceras;
- número de observaciones;
- tipos de datos;
- cobertura temporal;
- variables disponibles.

La principal diferencia estructural detectada es que el fichero de 2024 no contiene la columna `Ano`.

### 5.4. Revisión de variables

Los datasets contienen cinco grupos principales de variables:

#### Variables temporales

- año;
- mes;
- día;
- hora;
- minuto;
- fecha y hora completa.

#### Irradiancia solar

- `GHI`: irradiancia global horizontal;
- `DNI`: irradiancia directa normal;
- `DHI`: irradiancia difusa horizontal.

#### Variables meteorológicas

- temperatura;
- velocidad del viento;
- dirección del viento;
- humedad relativa.

#### Códigos de calidad

- código GHI;
- código DNI;
- código DHI.

Los códigos de calidad constituyen las variables objetivo iniciales del proyecto. Su interpretación exacta debe mantenerse vinculada a la documentación técnica de origen.

### 5.5. Cobertura temporal

Los datasets contienen una observación por minuto:

| Año | Días | Registros esperados | Registros observados |
|---|---:|---:|---:|
| 2023 | 365 | 525.600 | 525.600 |
| 2024 | 366 | 527.040 | 527.040 |

No se detectaron fechas duplicadas y ambas series se encuentran ordenadas cronológicamente.

### 5.6. Valores ausentes

Los porcentajes principales observados son:

| Grupo de variables | 2023 | 2024 |
|---|---:|---:|
| Irradiancia | 0,34 % | 1,91 % |
| Variables meteorológicas | 3,92 % | 14,15 % |

La ausencia de datos es considerablemente mayor en 2024, especialmente en temperatura, humedad y variables de viento. Esta diferencia deberá tenerse en cuenta durante la preparación de datos, la definición de las muestras válidas y la evaluación de los modelos.

### 5.7. Estadística descriptiva

Se revisan las estadísticas básicas de las variables numéricas:

- número de observaciones válidas;
- media;
- desviación estándar;
- mínimo;
- cuartiles;
- máximo.

No se observan valores negativos en las variables de irradiancia. No obstante, la ausencia de valores negativos no garantiza por sí sola la validez física de una medición. La coherencia debe evaluarse posteriormente frente a:

- elevación solar;
- condición día/noche;
- continuidad temporal;
- relaciones físicas entre GHI, DNI y DHI;
- códigos de calidad proporcionados.

### 5.8. Distribución de códigos de calidad

Distribución observada:

#### GHI

| Código | 2023 | 2024 |
|---:|---:|---:|
| 0 | 462.926 | 437.044 |
| 1 | 62.674 | 89.996 |

#### DNI

| Código | 2023 | 2024 |
|---:|---:|---:|
| 0 | 503.758 | 439.910 |
| 1 | 20.760 | 86.287 |
| 2 | 1.082 | 843 |

#### DHI

| Código | 2023 | 2024 |
|---:|---:|---:|
| 0 | 467.954 | 392.052 |
| 1 | 57.464 | 134.782 |
| 2 | 182 | 206 |

Estas distribuciones muestran un desequilibrio entre clases y diferencias relevantes entre años. Por tanto, la evaluación futura no debe basarse únicamente en `accuracy`. Será necesario priorizar métricas como `precision`, `recall`, `F1-score`, matrices de confusión y, según la formulación final del problema, `PR-AUC`.

### 5.9. Revisión de valores potencialmente anómalos

En 2024 aparecen registros de temperatura de hasta `-50 °C`. Este valor resulta poco plausible para la localización analizada y puede representar:

- un código interno de error;
- un valor de relleno del sistema de adquisición;
- un fallo del sensor;
- un dato físicamente inválido.

No debe eliminarse automáticamente sin comprobar antes la convención utilizada por la fuente. Debe registrarse como anomalía candidata para el preprocesamiento.

### 5.10. Inspección de la elevación solar de 2023

El fichero de elevación solar contiene:

- 525.600 observaciones válidas de 2023;
- un registro adicional con fecha `2024-01-01 00:00:00`;
- valores ausentes en `Mes` y `altura` en dicho registro adicional.

El registro final no corresponde al periodo objetivo de 2023 y debe eliminarse antes de generar el fichero estandarizado definitivo.

## 6. Salidas

El notebook genera:

```text
reports/tables/data_inventory.csv
```

Este fichero resume la estructura y calidad global de cada Excel localizado.

El notebook no genera todavía datasets transformados. Los datos originales deben permanecer sin cambios en `data/raw`.

## 7. Principales conclusiones

1. Los datos de 2023 y 2024 presentan cobertura completa a nivel temporal, con una observación por minuto.
2. No existen timestamps duplicados y las series están ordenadas.
3. El fichero de 2024 necesita incorporar la columna de año para igualar el esquema de 2023.
4. La proporción de valores ausentes aumenta de forma notable en 2024.
5. Existen temperaturas potencialmente inválidas, especialmente el valor `-50 °C`.
6. Los códigos de calidad presentan desequilibrio entre clases.
7. El fichero de elevación solar incluye un registro adicional que debe eliminarse.
8. La calidad física de las irradiancias no puede determinarse únicamente con estadística descriptiva; requiere elevación solar y reglas de coherencia.

## 8. Limitaciones del notebook

- No valida todavía la continuidad temporal mediante diferencias entre timestamps consecutivos.
- No diferencia entre datos ausentes, códigos de error y valores físicamente imposibles.
- No transforma los códigos de calidad en targets definitivos.
- No comprueba las relaciones físicas entre GHI, DNI, DHI y elevación solar.
- No genera gráficos exploratorios.
- La selección de `sample_2023` y `sample_2024` depende de que los nombres contengan `2023.xlsx` y `2024.xlsx`.
- El directorio `reports/tables` debe existir antes de ejecutar la exportación o debe crearse explícitamente.

## 9. Ejecución recomendada

El notebook debe ejecutarse desde la carpeta `notebooks/` y con la siguiente estructura mínima:

```text
project/
├── data/
│   └── raw/
│       ├── datos_2023.xlsx
│       ├── datos_2024.xlsx
│       └── altura_min_sevilla.xlsx
├── notebooks/
│   └── 01_data_inventory.ipynb
└── reports/
    └── tables/
```

Orden de ejecución:

```text
01_data_inventory.ipynb
02_column_preprocessing.ipynb
03_initial_eda.ipynb
```

## 10. Criterio de finalización

El inventario se considera completado cuando:

- todos los ficheros esperados aparecen en `data_inventory.csv`;
- las dimensiones se corresponden con la frecuencia temporal prevista;
- se han documentado las diferencias de esquema;
- se han identificado valores ausentes y anomalías candidatas;
- se ha comprobado que las fechas no están duplicadas;
- se han registrado las decisiones pendientes para el preprocesamiento.
