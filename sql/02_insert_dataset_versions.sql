-- ============================================================
-- Registro de versiones de datasets del proyecto
-- Base de datos: solar_irradiance_db
-- Esquema: solar
-- Tabla: solar.dataset_versions
-- ============================================================

INSERT INTO solar.dataset_versions (
    version_name,
    source_file,
    file_path,
    file_format,
    processing_stage,
    description,
    period_start,
    period_end,
    row_count,
    column_count,
    ready_for_modeling,
    loaded_in_database
)
VALUES
    (
        'raw_datos_2023',
        'datos_2023.xlsx',
        'data/raw/datos_2023.xlsx',
        'xlsx',
        'raw',
        'Datos originales de irradiancia y variables asociadas correspondientes al año 2023.',
        '2023-01-01 00:00:00',
        '2023-12-31 23:59:00',
        NULL,
        NULL,
        FALSE,
        FALSE
    ),
    (
        'raw_alturas_2023',
        'alturas_2023.xlsx',
        'data/raw/alturas_2023.xlsx',
        'xlsx',
        'raw',
        'Datos originales de altura o elevación solar correspondientes al año 2023.',
        '2023-01-01 00:00:00',
        '2023-12-31 23:59:00',
        NULL,
        NULL,
        FALSE,
        FALSE
    ),
    (
        'raw_datos_2024',
        'datos_2024.xlsx',
        'data/raw/datos_2024.xlsx',
        'xlsx',
        'raw',
        'Datos originales de irradiancia y variables asociadas correspondientes al año 2024.',
        '2024-01-01 00:00:00',
        '2024-12-31 23:59:00',
        NULL,
        NULL,
        FALSE,
        FALSE
    ),
    (
        'interim_datos_2023_standardized',
        'datos_2023_standardized.parquet',
        'data/interim/datos_2023_standardized.parquet',
        'parquet',
        'interim',
        'Datos de 2023 con nombres de columnas, tipos y formato temporal estandarizados.',
        '2023-01-01 00:00:00',
        '2023-12-31 23:59:00',
        NULL,
        NULL,
        FALSE,
        FALSE
    ),
    (
        'interim_datos_2024_standardized',
        'datos_2024_standardized.parquet',
        'data/interim/datos_2024_standardized.parquet',
        'parquet',
        'interim',
        'Datos de 2024 con nombres de columnas, tipos y formato temporal estandarizados.',
        '2024-01-01 00:00:00',
        '2024-12-31 23:59:00',
        NULL,
        NULL,
        FALSE,
        FALSE
    ),
    (
        'interim_elevacion_2023_standardized',
        'elevacion_2023_standardized.parquet',
        'data/interim/elevacion_2023_standardized.parquet',
        'parquet',
        'interim',
        'Datos de elevación solar de 2023 estandarizados y preparados para su integración.',
        '2023-01-01 00:00:00',
        '2023-12-31 23:59:00',
        NULL,
        NULL,
        FALSE,
        FALSE
    ),
    (
        'interim_elevacion_2024_standardized',
        'elevacion_2024_standardized.parquet',
        'data/interim/elevacion_2024_standardized.parquet',
        'parquet',
        'interim',
        'Datos de elevación solar de 2024 estandarizados y preparados para su integración.',
        '2024-01-01 00:00:00',
        '2024-12-31 23:59:00',
        NULL,
        NULL,
        FALSE,
        FALSE
    ),
    (
        'processed_dataset_solar_v1',
        'dataset_solar_2023_2024_v1.parquet',
        'data/processed/dataset_solar_2023_2024_v1.parquet',
        'parquet',
        'processed',
        'Primera versión integrada del dataset solar de 2023 y 2024 tras el preprocesamiento inicial.',
        '2023-01-01 00:00:00',
        '2024-12-31 23:59:00',
        NULL,
        NULL,
        FALSE,
        FALSE
    ),
    (
        'processed_dataset_solar_v2',
        'dataset_solar_2023_2024_v2.parquet',
        'data/processed/dataset_solar_2023_2024_v2.parquet',
        'parquet',
        'processed',
        'Segunda versión del dataset solar tras el análisis exploratorio y la generación de variables derivadas.',
        '2023-01-01 00:00:00',
        '2024-12-31 23:59:00',
        NULL,
        NULL,
        FALSE,
        FALSE
    ),
    (
        'processed_dataset_solar_v3',
        'dataset_solar_2023_2024_v3.parquet',
        'data/processed/dataset_solar_2023_2024_v3.parquet',
        'parquet',
        'processed',
        'Versión procesada vigente tras la imputación de valores nulos meteorológicos y preparada para su uso en modelado.',
        '2023-01-01 00:00:00',
        '2024-12-31 23:59:00',
        1052640,
        27,
        TRUE,
        FALSE
    )
ON CONFLICT (version_name) DO UPDATE
SET
    source_file = EXCLUDED.source_file,
    file_path = EXCLUDED.file_path,
    file_format = EXCLUDED.file_format,
    processing_stage = EXCLUDED.processing_stage,
    description = EXCLUDED.description,
    period_start = EXCLUDED.period_start,
    period_end = EXCLUDED.period_end,
    row_count = EXCLUDED.row_count,
    column_count = EXCLUDED.column_count,
    ready_for_modeling = EXCLUDED.ready_for_modeling,
    loaded_in_database = solar.dataset_versions.loaded_in_database;

-- Comprobación del registro
SELECT
    dataset_version_id,
    version_name,
    processing_stage,
    file_path,
    row_count,
    column_count,
    ready_for_modeling,
    loaded_in_database
FROM solar.dataset_versions
ORDER BY dataset_version_id;
