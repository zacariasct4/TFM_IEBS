-- ============================================================
-- Creación de tablas para el registro de experimentos
-- Base de datos: solar_irradiance_db
-- Esquema: solar
--
-- Este script crea las tablas necesarias para registrar:
--   1. La configuración de cada experimento de modelado.
--   2. Las variables objetivo y predictoras utilizadas.
--   3. Los hiperparámetros y particiones temporales.
--   4. Las métricas obtenidas en cada ejecución.
--   5. La ruta del modelo entrenado y su estado.
--
-- Tablas creadas:
--   - solar.model_experiments
--   - solar.model_metrics
--
-- Orden de ejecución recomendado:
--   1. 01_create_tables.sql
--   2. 02_insert_dataset_versions.sql
--   3. 03_create_indexes.sql
--   4. 04_create_views.sql
--   5. 05_create_experiment_tables.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS solar.model_experiments (
    experiment_id INTEGER GENERATED ALWAYS AS IDENTITY,
    dataset_version_id INTEGER NOT NULL,
    experiment_name VARCHAR(150) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    target_variable VARCHAR(50) NOT NULL,
    data_source VARCHAR(150),
    feature_columns JSONB NOT NULL,
    hyperparameters JSONB,
    train_start TIMESTAMP WITHOUT TIME ZONE,
    train_end TIMESTAMP WITHOUT TIME ZONE,
    validation_start TIMESTAMP WITHOUT TIME ZONE,
    validation_end TIMESTAMP WITHOUT TIME ZONE,
    test_start TIMESTAMP WITHOUT TIME ZONE,
    test_end TIMESTAMP WITHOUT TIME ZONE,
    random_seed INTEGER,
    execution_time_seconds DOUBLE PRECISION,
    model_path VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'planned',
    notes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_model_experiments
        PRIMARY KEY (experiment_id),

    CONSTRAINT fk_model_experiments_dataset_version
        FOREIGN KEY (dataset_version_id)
        REFERENCES solar.dataset_versions(dataset_version_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_model_experiments_name
        UNIQUE (experiment_name),

    CONSTRAINT chk_model_experiments_status
        CHECK (
            status IN (
                'planned',
                'running',
                'completed',
                'failed'
            )
        ),

    CONSTRAINT chk_model_experiments_execution_time
        CHECK (
            execution_time_seconds IS NULL
            OR execution_time_seconds >= 0
        ),

    CONSTRAINT chk_model_experiments_train_period
        CHECK (
            train_start IS NULL
            OR train_end IS NULL
            OR train_start <= train_end
        ),

    CONSTRAINT chk_model_experiments_validation_period
        CHECK (
            validation_start IS NULL
            OR validation_end IS NULL
            OR validation_start <= validation_end
        ),

    CONSTRAINT chk_model_experiments_test_period
        CHECK (
            test_start IS NULL
            OR test_end IS NULL
            OR test_start <= test_end
        )
);

CREATE TABLE IF NOT EXISTS solar.model_metrics (
    metric_id INTEGER GENERATED ALWAYS AS IDENTITY,
    experiment_id INTEGER NOT NULL,
    dataset_split VARCHAR(20) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    target_class VARCHAR(50),
    fold_number SMALLINT,
    notes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_model_metrics
        PRIMARY KEY (metric_id),

    CONSTRAINT fk_model_metrics_experiment
        FOREIGN KEY (experiment_id)
        REFERENCES solar.model_experiments(experiment_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT chk_model_metrics_dataset_split
        CHECK (
            dataset_split IN (
                'train',
                'validation',
                'test',
                'cross_validation'
            )
        ),

    CONSTRAINT chk_model_metrics_fold_number
        CHECK (
            fold_number IS NULL
            OR fold_number > 0
        )
);

CREATE INDEX IF NOT EXISTS idx_experiments_dataset_version
ON solar.model_experiments (dataset_version_id);

CREATE INDEX IF NOT EXISTS idx_experiments_model_name
ON solar.model_experiments (model_name);

CREATE INDEX IF NOT EXISTS idx_experiments_target_variable
ON solar.model_experiments (target_variable);

CREATE INDEX IF NOT EXISTS idx_experiments_status
ON solar.model_experiments (status);

CREATE INDEX IF NOT EXISTS idx_experiments_created_at
ON solar.model_experiments (created_at);

CREATE INDEX IF NOT EXISTS idx_metrics_experiment
ON solar.model_metrics (experiment_id);

CREATE INDEX IF NOT EXISTS idx_metrics_name
ON solar.model_metrics (metric_name);

CREATE INDEX IF NOT EXISTS idx_metrics_dataset_split
ON solar.model_metrics (dataset_split);

ALTER TABLE solar.model_experiments
OWNER TO solar_tfm_user;

ALTER TABLE solar.model_metrics
OWNER TO solar_tfm_user;

GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLE solar.model_experiments
TO solar_tfm_user;

GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLE solar.model_metrics
TO solar_tfm_user;

GRANT USAGE, SELECT, UPDATE
ON ALL SEQUENCES IN SCHEMA solar
TO solar_tfm_user;

SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'solar'
  AND table_name IN (
      'model_experiments',
      'model_metrics'
  )
ORDER BY table_name;
