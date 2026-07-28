# 08. Generación de gráficas diarias

## Objetivo

Generar las representaciones gráficas asociadas a cada documento diario de MongoDB y almacenar sus rutas y metadatos dentro del documento correspondiente.

Las imágenes se guardan como archivos PNG en el sistema de archivos del proyecto. MongoDB no almacena directamente los archivos binarios, sino la información necesaria para localizarlos y reutilizarlos posteriormente.

En esta fase se utiliza únicamente una fecha de prueba antes de automatizar la generación para todo el conjunto de datos.

## Arquitectura utilizada

El notebook reutiliza funciones definidas en la carpeta `src`:

- `get_database_engine()`: crea la conexión con PostgreSQL.
- `load_daily_measurements()`: recupera las mediciones del día seleccionado.
- `build_daily_document()`: reconstruye el documento diario.
- `generate_solar_curves_plot()`: genera la gráfica de curvas solares.
- `generate_quality_weather_plot()`: genera la gráfica de calidad, meteorología y procesamiento.

## Preparación de los datos

Se recuperan desde PostgreSQL los 1.440 registros correspondientes al día de prueba:

```text
2023-07-15
```

La columna `fecha` se convierte a formato `datetime` y se utiliza como referencia temporal para las gráficas.

También se crea la columna auxiliar `hora_local`, utilizada como eje temporal de las representaciones.

## Directorio de salida

Las imágenes se guardan siguiendo una estructura organizada por año:

```text
outputs/
└── daily_plots/
    └── 2023/
```

Para la fecha de prueba se generan los archivos:

```text
2023-07-15_solar_curves.png
2023-07-15_quality_weather.png
```

## Gráfica de curvas solares

La primera imagen representa la evolución diaria de:

- GHI;
- DNI;
- DHI;
- GHI estimado;
- elevación solar;
- mediciones identificadas mediante los códigos de calidad.

Esta gráfica permite analizar visualmente la forma de las curvas solares y detectar comportamientos inconsistentes o mediciones potencialmente incorrectas.

## Gráfica de calidad y meteorología

La segunda imagen representa:

- temperatura;
- humedad relativa;
- velocidad del viento;
- `codigo_ghi`;
- `codigo_dni`;
- `codigo_dhi`;
- indicador de imputación meteorológica;
- indicador de irradiancia originalmente nula.

Esta visualización relaciona las condiciones meteorológicas, la calidad de las mediciones y las transformaciones aplicadas durante el preprocesamiento.

## Actualización del documento diario

Tras generar las imágenes, se actualiza el bloque `graficas` del documento diario con:

- disponibilidad del archivo;
- ruta relativa;
- formato;
- fecha de generación.

También se actualiza la marca temporal `updated_at` del documento.

La estructura almacenada sigue el siguiente esquema:

```text
graficas
├── curvas_solares
│   ├── disponible
│   ├── ruta
│   ├── formato
│   └── fecha_generacion
└── calidad_meteorologia
    ├── disponible
    ├── ruta
    ├── formato
    └── fecha_generacion
```

## Compatibilidad con MongoDB

Después de añadir los metadatos de las imágenes, el documento se vuelve a serializar en formato BSON.

La validación confirma que el documento actualizado sigue siendo compatible con MongoDB y que su tamaño es muy inferior al límite máximo permitido por documento.

## Resultado

Se han generado dos representaciones gráficas para una fecha de prueba:

- curvas solares diarias;
- calidad, meteorología e indicadores de procesamiento.

Las imágenes se almacenan como archivos PNG y el documento diario conserva únicamente sus rutas y metadatos.

El documento queda preparado para su posterior inserción en MongoDB Atlas. En esta fase todavía no se han generado las gráficas para todas las fechas ni se ha realizado ninguna inserción en la base de datos.
