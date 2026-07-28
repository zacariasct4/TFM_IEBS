# 07. Construcción de documentos de resumen diario

## Objetivo

Construir y validar la estructura documental que se utilizará en MongoDB para almacenar un resumen por cada día del conjunto de datos solar.

Los registros minuto a minuto se recuperan desde PostgreSQL y se transforman en un único documento diario. En esta fase se trabaja con una fecha de prueba y todavía no se insertan documentos en MongoDB.

## Arquitectura utilizada

El notebook reutiliza funciones definidas en la carpeta `src`:

- `get_database_engine()`: crea la conexión con PostgreSQL.
- `load_daily_measurements()`: recupera las mediciones correspondientes a una fecha.
- `build_daily_document()`: transforma los registros del día en un documento compatible con MongoDB.

Esta separación permite mantener los notebooks centrados en la ejecución y validación del proceso, mientras que la lógica reutilizable permanece en módulos Python independientes.

## Extracción del día de prueba

Se utiliza como fecha de prueba:

```text
2023-07-15
```

Desde la tabla `solar.measurements` se recuperan 1.440 registros, correspondientes a las mediciones minuto a minuto de un día completo.

Las comprobaciones iniciales verifican:

- número de registros;
- fecha mínima y máxima;
- número de columnas;
- ausencia de fechas duplicadas.

## Estructura del documento diario

El documento diario incluye los siguientes bloques:

### Identificación y periodo

- fecha del documento;
- versión del dataset;
- origen de los datos;
- año, mes y día;
- día de la semana.

### Cobertura

- número total de registros;
- fecha inicial y final;
- número de fechas duplicadas;
- registros correspondientes al periodo diurno;
- registros correspondientes al periodo nocturno.

### Irradiancia

Se incluyen estadísticas descriptivas de:

- GHI;
- DNI;
- DHI;
- GHI estimado.

### Meteorología

Se resumen:

- temperatura;
- humedad relativa;
- velocidad del viento.

### Variables físicas

Se incluyen estadísticas de:

- elevación solar;
- error de balance;
- error de balance absoluto;
- error de balance relativo.

### Calidad

Se almacena la distribución diaria de:

- `codigo_ghi`;
- `codigo_dni`;
- `codigo_dhi`.

### Procesamiento

Se resumen los indicadores binarios:

- `var_meteo_imp`, que señala si al menos una variable meteorológica del registro fue imputada;
- `irr_null`, que indica si el registro presentaba originalmente alguna irradiancia nula.

### Estructuras futuras

El documento reserva campos para incorporar posteriormente:

- rutas y metadatos de las gráficas diarias;
- resultados diarios de los modelos;
- anomalías detectadas;
- explicaciones automáticas.

## Validaciones realizadas

El notebook comprueba que:

- el número de registros del documento coincide con el DataFrame original;
- la suma de registros diurnos y nocturnos coincide con el total diario;
- el número de fechas duplicadas es correcto;
- las distribuciones de los códigos de calidad suman el total de registros;
- los indicadores binarios suman el total diario;
- el documento puede serializarse correctamente en formato BSON.

## Resultado

Se ha transformado un día completo de mediciones procedentes de PostgreSQL en un documento diario compatible con MongoDB.

El documento queda preparado para incorporar posteriormente las gráficas, los resultados de los modelos, las anomalías y las explicaciones automáticas. En esta fase todavía no se ha insertado ningún documento en MongoDB Atlas.
