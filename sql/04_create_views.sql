-- ============================================================
-- Creación de vistas para modelado
-- Base de datos: solar_irradiance_db
-- Esquema: solar
--
-- Este archivo se ampliará progresivamente conforme se definan
-- los distintos experimentos y subconjuntos de variables.
-- Las vistas permiten reutilizar consultas sin duplicar datos.
-- ============================================================

CREATE OR REPLACE VIEW solar.vw_measurements_v3 AS
SELECT m.*
FROM solar.measurements AS m
INNER JOIN solar.dataset_versions AS dv
    ON m.dataset_version_id = dv.dataset_version_id
WHERE dv.version_name = 'processed_dataset_solar_v3';