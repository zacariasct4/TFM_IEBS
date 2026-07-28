# 06. Configuración y conexión con MongoDB Atlas

## Objetivo

Configurar y validar la conexión entre el proyecto y MongoDB Atlas mediante el driver oficial PyMongo.

MongoDB se utilizará como capa documental para almacenar resúmenes diarios de las mediciones solares, referencias a gráficas y, posteriormente, resúmenes visuales y explicativos de los resultados de los modelos. Los datos tabulares detallados y las predicciones a nivel de registro permanecerán almacenados en PostgreSQL.

## Configuración realizada

Las credenciales de MongoDB Atlas se almacenan en un archivo `.env` excluido del control de versiones. De esta forma, la conexión puede establecerse sin incluir información sensible directamente en el código.

Las variables utilizadas son:

- `MONGODB_URI`: cadena de conexión al clúster de MongoDB Atlas.
- `MONGODB_DATABASE`: nombre de la base de datos lógica del proyecto.

## Conexión con MongoDB Atlas

La conexión se establece mediante `MongoClient`, utilizando la Stable API de MongoDB y un tiempo máximo de espera para la selección del servidor.

La disponibilidad del clúster y la validez de las credenciales se comprueban mediante una operación `ping` sobre la base de datos administrativa.

## Selección de la base de datos

Tras verificar la conexión, se selecciona la base de datos lógica:

```text
solar_irradiance_db
```

La selección de la base de datos no implica todavía su creación física. MongoDB materializará la base de datos cuando se inserte el primer documento.

## Comprobaciones realizadas

El notebook verifica:

- la carga correcta de las variables de entorno;
- la disponibilidad de la URI y del nombre de la base de datos;
- la conexión con el clúster de MongoDB Atlas;
- el acceso a las bases de datos disponibles;
- el cierre correcto de la conexión.

## Resultado

La conexión con MongoDB Atlas queda configurada y validada mediante PyMongo.

En este punto todavía no se han creado colecciones ni insertado documentos. La creación efectiva de la base de datos y de la colección documental se realizará cuando se cargue el primer resumen diario.
