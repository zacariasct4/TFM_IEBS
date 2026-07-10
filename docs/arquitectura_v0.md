# Arquitectura inicial del proyecto

## Flujo general

Excel originales 2023/2024  
→ Ingesta con Python  
→ Estandarización de columnas y fechas  
→ Base de datos relacional PostgreSQL  
→ Procesamiento analítico con Python / PySpark  
→ Dataset final para Machine Learning  
→ Modelos de clasificación  
→ Evaluación e interpretación  
→ Visualizaciones y conclusiones

## Justificación

La arquitectura permite demostrar conocimientos de:
- ETL con Python.
- Bases de datos relacionales y SQL.
- Procesamiento de datos estructurados.
- Big Data / Spark si el volumen o el enfoque metodológico lo justifica.
- Machine Learning supervisado.
- Evaluación e interpretación de modelos.

## Papel de PostgreSQL

PostgreSQL se utilizará como repositorio estructurado de las mediciones limpias y trazables.

## Papel de Spark/PySpark

Spark/PySpark se podrá utilizar para simular o demostrar un procesamiento escalable sobre los datos históricos minuto a minuto.

## Papel de MongoDB

MongoDB queda como componente opcional para almacenar metadatos, resultados de validaciones, logs del pipeline o explicaciones generadas. No será la base principal porque los datos son altamente estructurados.