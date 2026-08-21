from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database.connection import get_database_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "dataset_solar_2023_2024_v3.parquet"
)

VERSION_NAME = "processed_dataset_solar_v3"

CHUNK_SIZE = 2_000


def get_dataset_version_id(connection) -> int:
    """Obtener el identificador de la versión v3 registrada."""

    query = text(
        """
        SELECT dataset_version_id
        FROM solar.dataset_versions
        WHERE version_name = :version_name;
        """
    )

    result = connection.execute(
        query,
        {"version_name": VERSION_NAME},
    ).scalar_one_or_none()

    if result is None:
        raise ValueError(
            f"No existe la versión '{VERSION_NAME}' "
            "en solar.dataset_versions."
        )

    return result


def validate_dataset(df: pd.DataFrame) -> None:
    """Comprobar que el dataset contiene la estructura esperada."""

    expected_columns = [
        "ano",
        "mes_sin",
        "mes_cos",
        "dia",
        "hora_sin",
        "hora_cos",
        "minuto",
        "fecha",
        "ghi",
        "dni",
        "dhi",
        "ghi_estimado",
        "irr_null",
        "error_balance",
        "error_balance_abs",
        "error_balance_rel",
        "elevacion_solar",
        "periodo_solar",
        "temperatura",
        "velocidad_viento",
        "humedad_relativa",
        "direccion_viento_sin",
        "direccion_viento_cos",
        "var_meteo_imp",
        "codigo_ghi",
        "codigo_dni",
        "codigo_dhi",
    ]

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    extra_columns = [
        column
        for column in df.columns
        if column not in expected_columns
    ]

    if missing_columns:
        raise ValueError(
            f"Faltan columnas en el dataset: {missing_columns}"
        )

    if extra_columns:
        raise ValueError(
            f"Existen columnas no esperadas: {extra_columns}"
        )

    if df["fecha"].isna().any():
        raise ValueError(
            "La columna 'fecha' contiene valores nulos."
        )

    duplicated_dates = df["fecha"].duplicated().sum()

    if duplicated_dates > 0:
        raise ValueError(
            f"Existen {duplicated_dates} fechas duplicadas."
        )


def load_measurements(replace: bool = False) -> None:
    """Cargar la versión v3 en PostgreSQL."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"No se encuentra el dataset: {DATASET_PATH}"
        )

    print("Leyendo dataset...")
    df = pd.read_parquet(DATASET_PATH)

    validate_dataset(df)

    engine = get_database_engine()

    with engine.begin() as connection:
        dataset_version_id = get_dataset_version_id(connection)

        existing_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM solar.measurements
                WHERE dataset_version_id = :dataset_version_id;
                """
            ),
            {"dataset_version_id": dataset_version_id},
        ).scalar_one()

        if existing_rows > 0:
            if not replace:
                raise ValueError(
                    f"La versión ya tiene {existing_rows:,} registros "
                    "cargados en solar.measurements."
                )

            print(
                f"Eliminando {existing_rows:,} registros existentes "
                "antes de recargar..."
            )

            connection.execute(
                text(
                    """
                    DELETE FROM solar.measurements
                    WHERE dataset_version_id = :dataset_version_id;
                    """
                ),
                {"dataset_version_id": dataset_version_id},
            )

        df_to_load = df.copy()

        df_to_load.insert(
            0,
            "dataset_version_id",
            dataset_version_id,
        )

        print(
            f"Cargando {len(df_to_load):,} registros "
            f"en bloques de {CHUNK_SIZE:,}..."
        )

        df_to_load.to_sql(
            name="measurements",
            con=connection,
            schema="solar",
            if_exists="append",
            index=False,
            chunksize=CHUNK_SIZE,
            method=None,
        )

        connection.execute(
            text(
                """
                UPDATE solar.dataset_versions
                SET
                    row_count = :row_count,
                    column_count = :column_count,
                    period_start = :period_start,
                    period_end = :period_end,
                    loaded_in_database = TRUE
                WHERE dataset_version_id = :dataset_version_id;
                """
            ),
            {
                "row_count": len(df),
                "column_count": len(df.columns),
                "period_start": df["fecha"].min(),
                "period_end": df["fecha"].max(),
                "dataset_version_id": dataset_version_id,
            },
        )

    print("Carga completada correctamente.")


if __name__ == "__main__":
    load_measurements(replace=False)