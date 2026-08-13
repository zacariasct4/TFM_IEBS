-- ============================================================
-- Creación de tablas de modelos y resultados del proyecto
-- Base de datos: solar_irradiance_db
-- Esquema: solar
--
-- Tablas:
--     - solar.models
--     - solar.results
--
-- La tabla solar.models almacena la configuración de cada
-- modelo entrenado para cada variable objetivo.
--
-- La tabla solar.results almacena las métricas obtenidas por
-- cada modelo, incluyendo también su nombre para facilitar
-- consultas y comparaciones posteriores.
--
-- Cada modelo está asociado a una versión del dataset mediante
-- dataset_version_id y cada resultado está asociado a su modelo
-- mediante model_id.
-- ============================================================


-- ============================================================
-- Tabla: solar.models
-- ============================================================

CREATE TABLE IF NOT EXISTS solar.models (
    model_id SERIAL PRIMARY KEY,

    dataset_version_id INTEGER NOT NULL
        REFERENCES solar.dataset_versions(dataset_version_id),

    model_name VARCHAR(100) NOT NULL,
    target VARCHAR(50) NOT NULL,

    train_year SMALLINT NOT NULL,
    test_year SMALLINT NOT NULL,

    n_features SMALLINT NOT NULL,
    features JSONB NOT NULL,
    hyperparameters JSONB,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        target IN (
            'codigo_ghi',
            'codigo_dni',
            'codigo_dhi'
        )
    )
);


-- ============================================================
-- Tabla: solar.results
-- ============================================================

CREATE TABLE IF NOT EXISTS solar.results (
    result_id SERIAL PRIMARY KEY,

    model_id INTEGER NOT NULL
        REFERENCES solar.models(model_id)
        ON DELETE CASCADE,

    model_name VARCHAR(100) NOT NULL,

    f1_macro DOUBLE PRECISION NOT NULL,
    balanced_accuracy DOUBLE PRECISION NOT NULL,
    f1_weighted DOUBLE PRECISION NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- Índices
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_models_dataset_version
ON solar.models(dataset_version_id);

CREATE INDEX IF NOT EXISTS idx_models_name
ON solar.models(model_name);

CREATE INDEX IF NOT EXISTS idx_models_target
ON solar.models(target);

CREATE INDEX IF NOT EXISTS idx_results_model_id
ON solar.results(model_id);

CREATE INDEX IF NOT EXISTS idx_results_model_name
ON solar.results(model_name);