# Ideación inicial del Global Project

## Problema identificado

Las mediciones solares minuto a minuto pueden contener errores, valores nulos, incoherencias físicas o anomalías temporales. Esto afecta a la fiabilidad de análisis posteriores relacionados con energía solar, predicción de irradiancia, control de calidad y toma de decisiones.

## Contexto

El proyecto se enmarca en el análisis de datos energéticos y meteorológicos. Se trabajará con datos históricos de irradiancia solar correspondientes a los años 2023 y 2024, junto con información auxiliar de altura solar en Sevilla.

## Solución propuesta

Se plantea desarrollar una solución basada en Data Science, Big Data e Inteligencia Artificial para integrar los datos originales, analizarlos, aplicar reglas de validación, construir variables explicativas y entrenar modelos capaces de clasificar mediciones correctas e incorrectas.

## Tipo de problema

Clasificación supervisada de calidad de datos, complementada con análisis exploratorio, reglas físicas y posible detección de anomalías.

## Valor del proyecto

La solución puede servir como herramienta de apoyo para sistemas de Business Intelligence energético, control de calidad de estaciones meteorológicas y análisis fiable de datos solares.

## Alcance inicial

El proyecto se centrará en:
- Ingesta y estructuración de datos Excel.
- Almacenamiento en base de datos.
- Análisis exploratorio.
- Validación de calidad.
- Modelos de clasificación.
- Evaluación e interpretación de resultados.

## Objetivo general provisional

Desarrollar una solución basada en Data Science, Big Data e Inteligencia Artificial para validar automáticamente mediciones solares minuto a minuto, clasificando la calidad de las variables H, GHI y DNI a partir de datos históricos, variables solares auxiliares y modelos de aprendizaje automático.

## Objetivos específicos provisionales

1. Integrar y estructurar los datos históricos de irradiancia solar procedentes de archivos Excel en una arquitectura reproducible de almacenamiento y procesamiento.

2. Realizar un análisis exploratorio y de calidad de datos para identificar valores nulos, incoherencias físicas, patrones temporales y posibles anomalías.

3. Desarrollar modelos de clasificación supervisada y/o detección de anomalías para determinar si las mediciones de H, GHI y DNI son correctas o incorrectas.

4. Evaluar e interpretar los resultados obtenidos mediante métricas estándar, visualizaciones y técnicas de explicabilidad orientadas a su aplicación en sistemas de BI energético.

