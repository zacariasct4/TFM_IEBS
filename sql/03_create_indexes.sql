-- ============================================================
-- Creación de índices para las consultas del proyecto
-- Base de datos: solar_irradiance_db
-- Esquema: solar
-- Tabla: solar.measurements
--
-- Los índices se limitan a variables que se utilizarán
-- frecuentemente para filtrar observaciones y preparar
-- subconjuntos destinados al modelado.
-- ============================================================

-- Consultas temporales dentro de una versión concreta
CREATE INDEX IF NOT EXISTS idx_measurements_version_fecha
ON solar.measurements (dataset_version_id, fecha);

-- Filtrado por año
CREATE INDEX IF NOT EXISTS idx_measurements_version_ano
ON solar.measurements (dataset_version_id, ano);

-- Filtrado entre periodo diurno y nocturno
CREATE INDEX IF NOT EXISTS idx_measurements_version_periodo
ON solar.measurements (dataset_version_id, periodo_solar);

-- Filtrado por clases objetivo
CREATE INDEX IF NOT EXISTS idx_measurements_codigo_ghi
ON solar.measurements (codigo_ghi);

CREATE INDEX IF NOT EXISTS idx_measurements_codigo_dni
ON solar.measurements (codigo_dni);

CREATE INDEX IF NOT EXISTS idx_measurements_codigo_dhi
ON solar.measurements (codigo_dhi);