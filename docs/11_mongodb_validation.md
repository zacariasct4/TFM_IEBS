# 11. Validación de la carga en MongoDB

## Objetivo

Validar la integridad y consistencia de los documentos diarios almacenados en MongoDB Atlas después de completar la carga masiva.

La validación compara las fechas disponibles en PostgreSQL con los documentos almacenados en MongoDB, comprueba la ausencia de fechas ausentes, inesperadas o duplicadas, verifica la cobertura temporal y revisa de forma muestral la estructura de los documentos y los metadatos de sus gráficas.

## Conexiones y configuración

El notebook utiliza:

- PostgreSQL, como fuente de referencia de las fechas disponibles;
- MongoDB Atlas, como almacenamiento de los documentos diarios;
- versión del dataset: `v3`;
- colección: `daily_summaries`.

## Recuento de documentos

PostgreSQL contiene 731 fechas disponibles y MongoDB almacena 731 documentos para la versión `v3`.

La igualdad entre ambos recuentos confirma que existe un documento por cada fecha procesada.

## Correspondencia de fechas

Se comparan los conjuntos de fechas de PostgreSQL y MongoDB.

Los resultados obtenidos son:

- fechas ausentes en MongoDB: 0;
- fechas inesperadas en MongoDB: 0;
- fechas duplicadas en MongoDB: 0.

Esto confirma que la colección contiene exactamente las mismas fechas que PostgreSQL.

## Cobertura temporal

El rango temporal coincide en ambas bases de datos:

```text
Primera fecha: 2023-01-01
Última fecha: 2024-12-31
```

Por tanto, la colección cubre completamente los dos años analizados.

## Validación muestral

Se seleccionan tres documentos representativos:

- primer día del conjunto;
- fecha intermedia;
- último día del conjunto.

Las fechas revisadas son:

```text
2023-01-01
2024-01-01
2024-12-31
```

En cada documento se comprueba la presencia de los bloques principales:

- fecha;
- información del dataset;
- cobertura;
- irradiancia;
- meteorología;
- calidad;
- procesamiento;
- gráficas;
- metadatos.

También se valida que:

- la versión del dataset sea `v3`;
- las dos gráficas estén disponibles;
- ambas contengan una ruta;
- el formato almacenado sea PNG.

## Resultado

La carga masiva en MongoDB Atlas ha quedado validada correctamente.

Los 731 documentos almacenados coinciden con las 731 fechas disponibles en PostgreSQL. No existen fechas ausentes, inesperadas ni duplicadas y el rango temporal coincide entre ambas bases de datos.

La revisión muestral confirma que los documentos conservan la estructura esperada y que incluyen los metadatos de las gráficas diarias.

Con estas comprobaciones, el bloque de MongoDB queda cerrado a nivel de carga, integridad y consistencia.
