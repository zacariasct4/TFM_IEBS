# 09. Inserción de documentos diarios en MongoDB

## Objetivo

Validar la persistencia de los documentos diarios en MongoDB Atlas a partir de los datos almacenados en PostgreSQL.

En esta fase se procesa una única fecha de prueba para comprobar correctamente:

- la conexión reutilizable con MongoDB;
- la creación del índice único;
- la construcción del documento diario;
- la generación de las referencias a las gráficas;
- la inserción mediante una operación `upsert`;
- la recuperación posterior del documento;
- la ausencia de duplicados al repetir la carga.

La carga masiva de todas las fechas se realizará en una fase posterior.

## Arquitectura utilizada

El notebook reutiliza funciones definidas en la carpeta `src`:

- `get_database_engine()`: crea la conexión con PostgreSQL.
- `load_daily_measurements()`: recupera las mediciones correspondientes a una fecha.
- `get_mongodb_database()`: establece y valida la conexión con MongoDB Atlas.
- `build_daily_document()`: construye el documento de resumen diario.
- `generate_solar_curves_plot()`: genera la gráfica de curvas solares.
- `generate_quality_weather_plot()`: genera la gráfica de calidad y meteorología.
- `create_daily_documents_index()`: crea el índice único de la colección.
- `upsert_daily_document()`: inserta o actualiza el documento diario sin generar duplicados.

Esta separación mantiene la lógica reutilizable en módulos Python y deja el notebook centrado en la ejecución y validación del flujo completo.

## Configuración de la prueba

Se utiliza una fecha de prueba:

```text
2023-07-15
```

También se define:

- versión del dataset: `v3`;
- colección de MongoDB: `daily_summaries`;
- directorio de salida para las gráficas diarias.

## Conexión con las bases de datos

El notebook establece dos conexiones:

- PostgreSQL, como fuente principal de los registros minuto a minuto;
- MongoDB Atlas, como capa documental para almacenar los resúmenes diarios.

La conexión con MongoDB se valida mediante una operación `ping` antes de continuar con la carga.

## Creación del índice único

Se crea un índice único formado por:

```text
fecha + dataset.version
```

Esta combinación permite identificar de manera unívoca cada documento diario.

El índice evita que se generen documentos duplicados para una misma fecha y versión del dataset, incluso si el proceso de carga se ejecuta varias veces.

## Extracción y preparación de los datos

Se recuperan desde PostgreSQL las mediciones correspondientes al día seleccionado.

Los datos se preparan para:

- construir el documento diario;
- generar las gráficas;
- crear la columna auxiliar `hora_local`;
- validar que las fechas sean correctas.

## Construcción del documento diario

El documento incluye:

- identificación de la fecha;
- versión y origen del dataset;
- cobertura diaria;
- estadísticas de irradiancia;
- resumen meteorológico;
- variables físicas;
- distribución de códigos de calidad;
- indicadores de procesamiento;
- estructuras preparadas para resultados de modelos, anomalías y explicaciones automáticas.

## Generación de las gráficas

Se generan dos archivos PNG:

- curvas solares diarias;
- calidad, meteorología e indicadores de procesamiento.

El documento no almacena directamente las imágenes. En su lugar, incorpora:

- ruta del archivo;
- formato;
- disponibilidad;
- fecha de generación.

## Inserción mediante `upsert`

El documento se almacena mediante una operación `upsert`.

Este comportamiento permite:

- insertar el documento si todavía no existe;
- actualizarlo si ya existe otro con la misma fecha y versión.

La operación evita la creación de duplicados y facilita la reejecución del proceso.

## Recuperación desde MongoDB

Después de la inserción, el documento se recupera desde MongoDB para comprobar:

- que existe;
- que la fecha coincide;
- que la versión del dataset es correcta;
- que dispone de un identificador `_id`;
- que el contenido ha sido almacenado correctamente.

## Validación del segundo `upsert`

La operación `upsert` se ejecuta una segunda vez con el mismo documento.

Después se comprueba que:

- no se genera un nuevo identificador;
- sigue existiendo un único documento para la combinación de fecha y versión;
- la segunda ejecución no crea duplicados.

Es normal que `modified_count` sea igual a cero cuando el documento enviado es idéntico al que ya se encuentra almacenado.

## Resultado

Se ha validado la persistencia de un documento diario en MongoDB Atlas para una fecha de prueba.

El proceso ha permitido:

- establecer las conexiones con PostgreSQL y MongoDB;
- crear el índice único basado en la fecha y la versión del dataset;
- recuperar las mediciones correspondientes al día seleccionado;
- construir el documento de resumen diario;
- generar las gráficas y añadir sus rutas y metadatos;
- insertar el documento mediante una operación `upsert`;
- recuperar posteriormente el documento desde MongoDB;
- repetir el `upsert` sin generar documentos duplicados.

La combinación de los campos `fecha` y `dataset.version` identifica de manera unívoca cada documento diario. De esta forma, una nueva ejecución actualiza el documento existente en lugar de crear una copia adicional.

En esta fase se ha procesado únicamente una fecha de prueba. La carga de todas las fechas disponibles se realizará posteriormente mediante un proceso masivo con control individual de errores.
