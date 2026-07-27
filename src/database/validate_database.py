from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database.connection import get_database_engine


DATASET_PATH = Path(
    "data/processed/dataset_solar_2023_2024_v3.parquet"
)

VERSION_NAME = "processed_dataset_solar_v3"

COLUMNS_TO_VALIDATE = [
    "ghi",
    "dni",
    "dhi",
    "ghi_estimado",
    "error_balance",
    "error_balance_abs",
    "error_balance_rel",
    "temperatura",
    "velocidad_viento",
    "humedad_relativa",
    "direccion_viento_sin",
    "direccion_viento_cos",
]


def get_dataset_version_id(connection) -> int:
    """Obtiene el identificador de la versión registrada."""

    query = text(
        """
        SELECT dataset_version_id
        FROM solar.dataset_versions
        WHERE version_name = :version_name;
        """
    )

    dataset_version_id = connection.execute(
        query,
        {"version_name": VERSION_NAME},
    ).scalar_one_or_none()

    if dataset_version_id is None:
        raise ValueError(
            f"No existe la versión '{VERSION_NAME}' "
            "en solar.dataset_versions."
        )

    return dataset_version_id


def get_database_summary(
    connection,
    dataset_version_id: int,
) -> dict:
    """Obtiene las métricas principales de la tabla PostgreSQL."""

    query = text(
        """
        SELECT
            COUNT(*) AS row_count,
            COUNT(DISTINCT fecha) AS unique_dates,
            MIN(fecha) AS period_start,
            MAX(fecha) AS period_end
        FROM solar.measurements
        WHERE dataset_version_id = :dataset_version_id;
        """
    )

    result = connection.execute(
        query,
        {"dataset_version_id": dataset_version_id},
    ).mappings().one()

    return dict(result)


def get_duplicate_count(
    connection,
    dataset_version_id: int,
) -> int:
    """Cuenta las fechas duplicadas de la versión."""

    query = text(
        """
        SELECT COUNT(*)
        FROM (
            SELECT fecha
            FROM solar.measurements
            WHERE dataset_version_id = :dataset_version_id
            GROUP BY fecha
            HAVING COUNT(*) > 1
        ) AS duplicated_dates;
        """
    )

    return connection.execute(
        query,
        {"dataset_version_id": dataset_version_id},
    ).scalar_one()


def get_database_null_counts(
    connection,
    dataset_version_id: int,
) -> dict:
    """Obtiene el número de nulos por variable en PostgreSQL."""

    null_expressions = ",\n".join(
        [
            (
                f"COUNT(*) FILTER "
                f"(WHERE {column} IS NULL) AS {column}"
            )
            for column in COLUMNS_TO_VALIDATE
        ]
    )

    query = text(
        f"""
        SELECT
            {null_expressions}
        FROM solar.measurements
        WHERE dataset_version_id = :dataset_version_id;
        """
    )

    result = connection.execute(
        query,
        {"dataset_version_id": dataset_version_id},
    ).mappings().one()

    return dict(result)


def get_version_metadata(connection) -> dict:
    """Obtiene los metadatos registrados para la versión v3."""

    query = text(
        """
        SELECT
            version_name,
            row_count,
            column_count,
            period_start,
            period_end,
            ready_for_modeling,
            loaded_in_database
        FROM solar.dataset_versions
        WHERE version_name = :version_name;
        """
    )

    result = connection.execute(
        query,
        {"version_name": VERSION_NAME},
    ).mappings().one()

    return dict(result)


def compare_values(
    label: str,
    parquet_value,
    database_value,
) -> bool:
    """Compara dos valores y muestra el resultado."""

    valid = parquet_value == database_value
    status = "OK" if valid else "ERROR"

    print(
        f"[{status}] {label}: "
        f"Parquet={parquet_value} | "
        f"PostgreSQL={database_value}"
    )

    return valid


def validate_database() -> None:
    """Valida la carga de PostgreSQL frente al Parquet v3."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"No se encuentra el dataset: {DATASET_PATH}"
        )

    print("Leyendo dataset Parquet...")
    df = pd.read_parquet(DATASET_PATH)

    parquet_summary = {
        "row_count": len(df),
        "unique_dates": df["fecha"].nunique(),
        "period_start": df["fecha"].min(),
        "period_end": df["fecha"].max(),
        "duplicate_dates": df["fecha"].duplicated().sum(),
    }

    parquet_null_counts = (
        df[COLUMNS_TO_VALIDATE]
        .isna()
        .sum()
        .to_dict()
    )

    engine = get_database_engine()

    with engine.connect() as connection:
        dataset_version_id = get_dataset_version_id(connection)

        database_summary = get_database_summary(
            connection,
            dataset_version_id,
        )

        database_duplicate_count = get_duplicate_count(
            connection,
            dataset_version_id,
        )

        database_null_counts = get_database_null_counts(
            connection,
            dataset_version_id,
        )

        version_metadata = get_version_metadata(connection)

    print("\nVALIDACIÓN GENERAL")
    print("-" * 70)

    validations = [
        compare_values(
            "Número de filas",
            parquet_summary["row_count"],
            database_summary["row_count"],
        ),
        compare_values(
            "Fechas únicas",
            parquet_summary["unique_dates"],
            database_summary["unique_dates"],
        ),
        compare_values(
            "Fecha inicial",
            parquet_summary["period_start"],
            database_summary["period_start"],
        ),
        compare_values(
            "Fecha final",
            parquet_summary["period_end"],
            database_summary["period_end"],
        ),
        compare_values(
            "Fechas duplicadas",
            parquet_summary["duplicate_dates"],
            database_duplicate_count,
        ),
    ]

    print("\nVALIDACIÓN DE NULOS")
    print("-" * 70)

    for column in COLUMNS_TO_VALIDATE:
        validations.append(
            compare_values(
                f"Nulos en {column}",
                int(parquet_null_counts[column]),
                int(database_null_counts[column]),
            )
        )

    print("\nMETADATOS DE LA VERSIÓN")
    print("-" * 70)

    validations.extend(
        [
            compare_values(
                "Filas registradas en dataset_versions",
                parquet_summary["row_count"],
                version_metadata["row_count"],
            ),
            compare_values(
                "Columnas registradas",
                len(df.columns),
                version_metadata["column_count"],
            ),
            compare_values(
                "Estado loaded_in_database",
                True,
                version_metadata["loaded_in_database"],
            ),
        ]
    )

    print("\nRESULTADO FINAL")
    print("-" * 70)

    if all(validations):
        print(
            "Validación completada correctamente. "
            "El Parquet y PostgreSQL son coherentes."
        )
    else:
        raise ValueError(
            "La validación ha detectado diferencias entre "
            "el Parquet y PostgreSQL."
        )


if __name__ == "__main__":
    validate_database()