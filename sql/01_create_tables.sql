-- ============================================================
-- Creación de tablas del proyecto
-- Base de datos: solar_irradiance_db
-- Esquema: solar
-- Tablas:
--   - solar.dataset_versions
--   - solar.measurements
--
-- Este script crea la estructura relacional para registrar
-- las versiones de los datasets y almacenar las mediciones
-- solares minuto a minuto con sus restricciones de integridad.
-- ============================================================

CREATE TABLE IF NOT EXISTS solar.dataset_versions (
    dataset_version_id INTEGER GENERATED ALWAYS AS IDENTITY,
    version_name VARCHAR(50) NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_format VARCHAR(20) NOT NULL,
    processing_stage VARCHAR(30) NOT NULL,
    description TEXT,
    period_start TIMESTAMP WITHOUT TIME ZONE,
    period_end TIMESTAMP WITHOUT TIME ZONE,
    row_count INTEGER,
    column_count SMALLINT,
    ready_for_modeling BOOLEAN NOT NULL DEFAULT FALSE,
    loaded_in_database BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_dataset_versions
        PRIMARY KEY (dataset_version_id),

    CONSTRAINT uq_dataset_versions_version_name
        UNIQUE (version_name),

    CONSTRAINT chk_dataset_versions_processing_stage
        CHECK (processing_stage IN ('raw', 'interim', 'processed')),

    CONSTRAINT chk_dataset_versions_file_format
        CHECK (file_format IN ('xlsx', 'csv', 'parquet')),

    CONSTRAINT chk_dataset_versions_row_count
        CHECK (row_count IS NULL OR row_count >= 0),

    CONSTRAINT chk_dataset_versions_column_count
        CHECK (column_count IS NULL OR column_count > 0),

    CONSTRAINT chk_dataset_versions_period
        CHECK (
            period_start IS NULL
            OR period_end IS NULL
            OR period_start <= period_end
        ),

    CONSTRAINT chk_dataset_versions_loaded_ready
        CHECK (
            loaded_in_database = FALSE
            OR processing_stage = 'processed'
        )
);

CREATE TABLE IF NOT EXISTS solar.measurements (
    dataset_version_id INTEGER NOT NULL,

    ano SMALLINT NOT NULL,
    mes_sin DOUBLE PRECISION NOT NULL,
    mes_cos DOUBLE PRECISION NOT NULL,
    dia SMALLINT NOT NULL,
    hora_sin DOUBLE PRECISION NOT NULL,
    hora_cos DOUBLE PRECISION NOT NULL,
    minuto SMALLINT NOT NULL,
    fecha TIMESTAMP WITHOUT TIME ZONE NOT NULL,

    ghi DOUBLE PRECISION,
    dni DOUBLE PRECISION,
    dhi DOUBLE PRECISION,
    ghi_estimado DOUBLE PRECISION,

    irr_null BOOLEAN NOT NULL,

    error_balance DOUBLE PRECISION,
    error_balance_abs DOUBLE PRECISION,
    error_balance_rel DOUBLE PRECISION,

    elevacion_solar DOUBLE PRECISION NOT NULL,
    periodo_solar VARCHAR(20) NOT NULL,

    temperatura DOUBLE PRECISION,
    velocidad_viento DOUBLE PRECISION,
    humedad_relativa DOUBLE PRECISION,
    direccion_viento_sin DOUBLE PRECISION,
    direccion_viento_cos DOUBLE PRECISION,

    var_meteo_imp BOOLEAN NOT NULL,

    codigo_ghi SMALLINT NOT NULL,
    codigo_dni SMALLINT NOT NULL,
    codigo_dhi SMALLINT NOT NULL,

    created_at TIMESTAMP WITHOUT TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_measurements
        PRIMARY KEY (dataset_version_id, fecha),

    CONSTRAINT fk_measurements_dataset_version
        FOREIGN KEY (dataset_version_id)
        REFERENCES solar.dataset_versions(dataset_version_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_measurements_year
        CHECK (ano BETWEEN 2000 AND 2100),

    CONSTRAINT chk_measurements_day
        CHECK (dia BETWEEN 1 AND 31),

    CONSTRAINT chk_measurements_minute
        CHECK (minuto BETWEEN 0 AND 59),

    CONSTRAINT chk_measurements_month_sin
        CHECK (mes_sin BETWEEN -1.000001 AND 1.000001),

    CONSTRAINT chk_measurements_month_cos
        CHECK (mes_cos BETWEEN -1.000001 AND 1.000001),

    CONSTRAINT chk_measurements_hour_sin
        CHECK (hora_sin BETWEEN -1.000001 AND 1.000001),

    CONSTRAINT chk_measurements_hour_cos
        CHECK (hora_cos BETWEEN -1.000001 AND 1.000001),

    CONSTRAINT chk_measurements_solar_elevation
        CHECK (elevacion_solar BETWEEN -90 AND 90),

    CONSTRAINT chk_measurements_periodo_solar
        CHECK (periodo_solar IN ('dia', 'noche')),

    CONSTRAINT chk_measurements_wind_speed
        CHECK (
            velocidad_viento IS NULL
            OR velocidad_viento >= 0
        ),

    CONSTRAINT chk_measurements_relative_humidity
        CHECK (
            humedad_relativa IS NULL
            OR humedad_relativa BETWEEN 0 AND 100
        ),

    CONSTRAINT chk_measurements_wind_direction_sin
        CHECK (
            direccion_viento_sin IS NULL
            OR direccion_viento_sin
                BETWEEN -1.000001 AND 1.000001
        ),

    CONSTRAINT chk_measurements_wind_direction_cos
        CHECK (
            direccion_viento_cos IS NULL
            OR direccion_viento_cos
                BETWEEN -1.000001 AND 1.000001
        ),

    CONSTRAINT chk_measurements_absolute_error
        CHECK (
            error_balance_abs IS NULL
            OR error_balance_abs >= 0
        ),

    CONSTRAINT chk_measurements_codigo_ghi
        CHECK (codigo_ghi IN (0, 1)),

    CONSTRAINT chk_measurements_codigo_dni
        CHECK (codigo_dni IN (0, 1, 2)),

    CONSTRAINT chk_measurements_codigo_dhi
        CHECK (codigo_dhi IN (0, 1, 2))
)

-- ============================================================
-- Asignación de propiedad y permisos al usuario del proyecto
-- ============================================================

ALTER TABLE solar.dataset_versions
OWNER TO solar_tfm_user;

ALTER TABLE solar.measurements
OWNER TO solar_tfm_user;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA solar
TO solar_tfm_user;

GRANT USAGE, SELECT, UPDATE
ON ALL SEQUENCES IN SCHEMA solar
TO solar_tfm_user;