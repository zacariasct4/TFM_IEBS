# 10. Carga masiva de documentos diarios en MongoDB

## Objetivo

Automatizar la construcción e inserción de los documentos diarios correspondientes a todas las fechas disponibles en PostgreSQL.

Cada fecha se procesa de forma independiente para evitar que un error puntual detenga la carga completa. El flujo reutiliza las funciones previamente validadas para:

- cargar los datos diarios desde PostgreSQL;
- construir el documento de resumen;
- generar las gráficas;
- añadir sus metadatos;
- insertar o actualizar el documento mediante `upsert`;
- registrar los días procesados correctamente y los días fallidos.

## Configuración del proceso

La carga utiliza:

- versión del dataset: `v3`;
- colección de MongoDB: `daily_summaries`;
- directorio de salida para las gráficas diarias;
- índice único basado en `fecha` y `dataset.version`.

La combinación de la fecha y la versión del dataset permite identificar de manera unívoca cada documento y evita duplicados durante las reejecuciones.

## Conexiones

El proceso establece conexiones con:

- PostgreSQL, como fuente de los registros minuto a minuto;
- MongoDB Atlas, como almacenamiento documental de los resúmenes diarios.

También se crea o recupera el índice único de la colección antes de comenzar la carga.

## Fechas disponibles

Las fechas se obtienen directamente desde PostgreSQL mediante `load_available_dates()`.

De esta forma, el proceso solo recorre fechas realmente presentes en la tabla de mediciones y no depende de un rango construido manualmente.

El conjunto procesado contiene 731 fechas comprendidas entre:

```text
2023-01-01
2024-12-31
```

## Procesamiento diario

Cada fecha se procesa mediante `process_daily_document()`.

La función realiza:

1. carga de las mediciones del día;
2. conversión y validación de la fecha;
3. construcción del documento diario;
4. generación de las dos gráficas;
5. validación de los archivos generados;
6. incorporación de rutas y metadatos;
7. inserción o actualización mediante `upsert`.

Los errores se capturan de manera individual para que una fecha fallida no interrumpa el procesamiento de las demás.

## Resultado de la carga

La carga completa ha finalizado con los siguientes resultados:

- fechas disponibles: 731;
- fechas procesadas correctamente: 731;
- fechas con error: 0;
- tiempo total aproximado: 38,70 minutos.

Cada día contiene 1.440 registros minuto a minuto.

## Validación posterior

Después de la carga se comprueba que:

- MongoDB contiene 731 documentos;
- el número de documentos coincide con el número de fechas procesadas;
- la primera fecha almacenada es `2023-01-01`;
- la última fecha almacenada es `2024-12-31`;
- no se han registrado errores durante la ejecución.

## Registro de ejecución

El proceso genera dos archivos CSV:

```text
outputs/mongodb_logs/mongodb_bulk_load_success.csv
outputs/mongodb_logs/mongodb_bulk_load_errors.csv
```

El primer archivo contiene el resultado de las fechas procesadas correctamente. El segundo almacena las fechas fallidas y sus errores, en caso de que existan.

## Resultado

Se ha completado la carga masiva de los documentos diarios en MongoDB Atlas.

Los 731 días disponibles en PostgreSQL se han transformado e insertado correctamente en la colección `daily_summaries`, sin errores y sin generar duplicados.

Cada documento incorpora el resumen diario, los indicadores de calidad, las variables meteorológicas y las referencias a las dos gráficas generadas para la fecha correspondiente.
