import os
import json
import pandas as pd
import psycopg2

from dotenv import load_dotenv

load_dotenv()


def get_postgresql_connection():
    """
    Crea y devuelve una conexión con la base de datos PostgreSQL
    utilizada en el proyecto.
    """

    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

def save_model_results_postgresql(
    results_df,
    model_name,
    dataset_version,
    features,
    hyperparameters=None,
    train_year=2024,
    test_year=2023
):

    if hyperparameters is None:
        hyperparameters = {}

    conn = get_postgresql_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT dataset_version_id
                FROM solar.dataset_versions
                WHERE version_name = %s;
                """,
                (dataset_version,)
            )

            dataset_row = cursor.fetchone()

            if dataset_row is None:
                raise ValueError(
                    f"No existe la versión '{dataset_version}' "
                    "en solar.dataset_versions."
                )

            dataset_version_id = dataset_row[0]

            model_ids = []

            for _, row in results_df.iterrows():

                cursor.execute(
                    """
                    INSERT INTO solar.models (
                        dataset_version_id,
                        model_name,
                        target,
                        train_year,
                        test_year,
                        n_features,
                        features,
                        hyperparameters
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING model_id;
                    """,
                    (
                        dataset_version_id,
                        model_name,
                        row["target"],
                        train_year,
                        test_year,
                        len(features),
                        json.dumps(features),
                        json.dumps(hyperparameters)
                    )
                )

                model_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO solar.results (
                        model_id,
                        model_name,
                        f1_macro,
                        balanced_accuracy,
                        f1_weighted
                    )
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        model_id,
                        model_name,
                        float(row["f1_macro"]),
                        float(row["balanced_accuracy"]),
                        float(row["f1_weighted"])
                    )
                )

                model_ids.append(model_id)

        conn.commit()

        print(
            f"{model_name} guardado correctamente "
            f"para {len(model_ids)} targets."
        )

        return model_ids

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def save_final_model_result_postgresql(
    result_row,
    model_name,
    dataset_version,
    features,
    hyperparameters,
    train_year,
    test_year,
):

    conn = get_postgresql_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT dataset_version_id
                FROM solar.dataset_versions
                WHERE version_name = %s;
                """,
                (dataset_version,)
            )

            dataset_row = cursor.fetchone()

            if dataset_row is None:
                raise ValueError(
                    f"No existe la versión "
                    f"'{dataset_version}'."
                )

            dataset_version_id = (
                dataset_row[0]
            )

            target = result_row["target"]

            cursor.execute(
                """
                SELECT model_id
                FROM solar.models
                WHERE dataset_version_id = %s
                  AND model_name = %s
                  AND target = %s
                  AND train_year = %s
                  AND test_year = %s
                ORDER BY model_id DESC
                LIMIT 1;
                """,
                (
                    dataset_version_id,
                    model_name,
                    target,
                    train_year,
                    test_year,
                )
            )

            existing = cursor.fetchone()

            if existing is None:

                cursor.execute(
                    """
                    INSERT INTO solar.models (
                        dataset_version_id,
                        model_name,
                        target,
                        train_year,
                        test_year,
                        n_features,
                        features,
                        hyperparameters
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    RETURNING model_id;
                    """,
                    (
                        dataset_version_id,
                        model_name,
                        target,
                        train_year,
                        test_year,
                        len(features),
                        json.dumps(features),
                        json.dumps(
                            hyperparameters
                        ),
                    )
                )

                model_id = cursor.fetchone()[0]

            else:

                model_id = existing[0]

                cursor.execute(
                    """
                    UPDATE solar.models
                    SET n_features = %s,
                        features = %s,
                        hyperparameters = %s
                    WHERE model_id = %s;
                    """,
                    (
                        len(features),
                        json.dumps(features),
                        json.dumps(
                            hyperparameters
                        ),
                        model_id,
                    )
                )

            cursor.execute(
                """
                DELETE FROM solar.results
                WHERE model_id = %s;
                """,
                (model_id,)
            )

            cursor.execute(
                """
                INSERT INTO solar.results (
                    model_id,
                    model_name,
                    f1_macro,
                    balanced_accuracy,
                    f1_weighted
                )
                VALUES (%s, %s, %s, %s, %s);
                """,
                (
                    model_id,
                    model_name,
                    float(
                        result_row["f1_macro"]
                    ),
                    float(
                        result_row[
                            "balanced_accuracy"
                        ]
                    ),
                    float(
                        result_row[
                            "f1_weighted"
                        ]
                    ),
                )
            )

        conn.commit()

        return model_id

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()