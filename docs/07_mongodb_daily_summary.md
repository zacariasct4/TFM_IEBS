# 07. Construcción de documentos de resumen diario

## Objetivo

Construir y validar la estructura documental que se utilizará en MongoDB para almacenar un resumen por cada día del conjunto de datos solar.

Los registros minuto a minuto se recuperan desde PostgreSQL y se transforman en un único documento diario. En esta fase se trabaja con una fecha de prueba y todavía no se insertan documentos en MongoDB.

## Origen de los datos

Los datos se recuperan desde:

```text
solar.measurements
```

La conexión con PostgreSQL se realiza mediante SQLAlchemy y las credenciales almacenadas en el archivo `.env`.

Para la fecha seleccionada se obtienen todos los registros ordenados cronológicamente y se comprueba:

- el número de registros;
- la fecha mínima y máxima;
- el número de columnas;
- la existencia de fechas duplicadas.

## Funciones auxiliares

Se crean funciones reutilizables para transformar los datos a una estructura compatible con MongoDB.

### Conversión de tipos

Los valores de NumPy y pandas se convierten a tipos nativos de Python para evitar incompatibilidades durante la serialización BSON.

### Resumen numérico

Para las variables continuas se calculan:

- media;
- mediana;
- mínimo;
- máximo;
- desviación estándar;
- número de valores nulos.

### Distribución categórica

Para los códigos de calidad se calcula:

- frecuencia absoluta de cada categoría;
- porcentaje diario de cada categoría.

### Resumen de indicadores binarios

Las variables `var_meteo_imp` e `irr_null` se tratan como indicadores binarios.

- `var_meteo_imp = 1` indica que al menos una variable meteorológica del registro fue imputada.
- `irr_null = 1` indica que el registro presentaba al menos una irradiancia nula antes del tratamiento.

Para cada indicador se almacenan:

- número de valores 0;
- número de valores 1;
- número de nulos;
- porcentaje de registros con valor 1.

## Estructura del documento diario

Cada documento contiene los siguientes bloques:

### Identificación y periodo

- fecha del documento;
- versión del dataset;
- año, mes y día;
- día de la semana.

### Cobertura

- número total de registros;
- fecha inicial y final;
- número de fechas duplicadas;
- registros correspondientes al periodo diurno;
- registros correspondientes al periodo nocturno.

### Irradiancia

Se resumen las variables:

- GHI;
- DNI;
- DHI;
- GHI estimado.

### Meteorología

Se resumen las variables:

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

Se resumen los indicadores:

- imputación meteorológica;
- presencia original de irradiancias nulas.

### Estructuras futuras

El documento reserva campos vacíos para incorporar posteriormente:

- rutas de las gráficas diarias;
- resultados diarios de los modelos;
- anomalías detectadas;
- explicaciones automáticas.

Los resultados detallados y las métricas globales de los modelos permanecerán almacenados en PostgreSQL. MongoDB contendrá únicamente su representación diaria, visual y contextual.

## Validaciones realizadas

El notebook comprueba que:

- el documento representa una única fecha;
- el número de registros coincide con el DataFrame original;
- la suma de registros diurnos y nocturnos coincide con el total;
- las distribuciones de calidad suman el total de registros;
- los indicadores binarios contienen valores válidos;
- las frecuencias de los indicadores suman el total diario;
- el documento puede serializarse correctamente en formato BSON.

## Resultado

Se ha transformado un día completo de mediciones procedentes de PostgreSQL en un documento de resumen diario compatible con MongoDB.

La estructura queda preparada para incorporar posteriormente las gráficas, los resultados diarios de los modelos, las anomalías y las explicaciones automáticas. En esta fase todavía no se ha insertado ningún documento en MongoDB.
