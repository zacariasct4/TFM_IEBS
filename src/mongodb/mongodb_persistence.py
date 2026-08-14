import numpy as np
import pandas as pd

from datetime import datetime, timezone

from sklearn.metrics import (
    f1_score,
    balanced_accuracy_score,
    confusion_matrix
)

from src.mongodb.connection import get_mongodb_database

TARGET_CLASSES = {
    "codigo_ghi": [0, 1],
    "codigo_dni": [0, 1, 2],
    "codigo_dhi": [0, 1, 2]
}

def build_daily_model_result(
    y_true,
    y_pred,
    model_id,
    model_name,
    target,
    dataset_version,
    n_features,
    train_year,
    test_year
):
    """
    Construye el resumen del rendimiento diario de un modelo
    para una variable objetivo concreta.
    """

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    # Clases presentes en valores reales o predichos
    classes = TARGET_CLASSES[target]

    # Distribución de códigos reales
    real_distribution = {
        str(int(cls)): int((y_true == cls).sum())
        for cls in classes
    }

    # Distribución de códigos predichos
    predicted_distribution = {
        str(int(cls)): int((y_pred == cls).sum())
        for cls in classes
    }

    # Matriz de confusión diaria
    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=classes
    )

    return {
        "postgresql_model_id": int(model_id),
        "modelo": model_name,
        "target": target,

        "dataset_version": dataset_version,
        "train_year": int(train_year),
        "test_year": int(test_year),
        "n_features": int(n_features),

        "metricas": {
            "f1_macro": float(
                f1_score(
                    y_true,
                    y_pred,
                    labels=classes,
                    average="macro",
                    zero_division=0
                )
            ),
            "balanced_accuracy": float(
                balanced_accuracy_score(
                    y_true,
                    y_pred
                )
            ),
            "f1_weighted": float(
                f1_score(
                    y_true,
                    y_pred,
                    labels=classes,
                    average="weighted",
                    zero_division=0
                )
            )
        },

        "clases": [
            int(cls)
            for cls in classes
        ],

        "distribucion_real": real_distribution,
        "distribucion_predicha": predicted_distribution,

        "matriz_confusion": matrix.tolist(),

        "updated_at": datetime.now(timezone.utc)
    }

def build_daily_model_result(
    y_true,
    y_pred,
    model_id,
    model_name,
    target,
    dataset_version,
    n_features,
    train_year,
    test_year
):
    """
    Construye el resumen del rendimiento diario de un modelo
    para una variable objetivo concreta.
    """

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    # Clases presentes en valores reales o predichos
    classes = sorted(
        set(y_true.tolist()) |
        set(y_pred.tolist())
    )

    # Distribución de códigos reales
    real_distribution = {
        str(int(cls)): int((y_true == cls).sum())
        for cls in classes
    }

    # Distribución de códigos predichos
    predicted_distribution = {
        str(int(cls)): int((y_pred == cls).sum())
        for cls in classes
    }

    # Matriz de confusión diaria
    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=classes
    )

    return {
        "postgresql_model_id": int(model_id),
        "modelo": model_name,
        "target": target,

        "dataset_version": dataset_version,
        "train_year": int(train_year),
        "test_year": int(test_year),
        "n_features": int(n_features),

        "metricas": {
            "f1_macro": float(
                f1_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0
                )
            ),
            "balanced_accuracy": float(
                balanced_accuracy_score(
                    y_true,
                    y_pred
                )
            ),
            "f1_weighted": float(
                f1_score(
                    y_true,
                    y_pred,
                    average="weighted",
                    zero_division=0
                )
            )
        },

        "clases": [
            int(cls)
            for cls in classes
        ],

        "distribucion_real": real_distribution,
        "distribucion_predicha": predicted_distribution,

        "matriz_confusion": matrix.tolist(),

        "updated_at": datetime.now(timezone.utc)
    }

def upsert_daily_model_result(
    collection,
    document_filter,
    model_result
):
    """
    Actualiza el resultado si el modelo ya existe en el documento
    diario o lo añade si todavía no ha sido registrado.
    """

    model_id = model_result["postgresql_model_id"]
    target = model_result["target"]

    # Intentar actualizar una ejecución existente
    result = collection.update_one(
        {
            **document_filter,
            "resultados_modelos.ejecuciones": {
                "$elemMatch": {
                    "postgresql_model_id": model_id,
                    "target": target
                }
            }
        },
        {
            "$set": {
                "resultados_modelos.ejecuciones.$": model_result,
                "resultados_modelos.disponible": True,
                "resultados_modelos.updated_at": datetime.now(
                    timezone.utc
                )
            }
        }
    )

    # Si no existe esa ejecución, añadirla
    if result.matched_count == 0:

        result = collection.update_one(
            document_filter,
            {
                "$set": {
                    "resultados_modelos.disponible": True,
                    "resultados_modelos.updated_at": datetime.now(
                        timezone.utc
                    )
                },
                "$push": {
                    "resultados_modelos.ejecuciones": model_result
                }
            }
        )

    return result

def save_model_results_mongodb(
    test_df,
    predictions,
    model_name,
    model_ids_by_target,
    dataset_version,
    features,
    targets,
    train_year,
    test_year,
    collection_name="daily_summaries"
):
    """
    Guarda en MongoDB los resultados diarios de un modelo
    para todos los targets evaluados.

    Los documentos diarios existentes se actualizan sin crear
    nuevos documentos ni duplicar ejecuciones.
    """

    db, client = get_mongodb_database()

    collection = db[collection_name]

    data = test_df.copy()

    try:

        # Añadir predicciones al dataframe de test
        for target in targets:

            if len(predictions[target]) != len(data):
                raise ValueError(
                    f"La longitud de las predicciones de {target} "
                    "no coincide con test_df."
                )

            data[f"pred_{target}"] = np.asarray(
                predictions[target]
            )

        success = []
        errors = []

        # Agrupar las observaciones minuto a minuto por fecha
        for date_value, daily_df in data.groupby(
            data["fecha"].dt.date
        ):

            try:

                # MongoDB utiliza datetime a las 00:00:00
                mongo_date = datetime(
                    date_value.year,
                    date_value.month,
                    date_value.day
                )

                document_filter = {
                    "fecha": mongo_date,
                    "dataset.version": dataset_version
                }

                # Comprobar que el documento diario existe
                existing_document = collection.find_one(
                    document_filter,
                    {"_id": 1}
                )

                if existing_document is None:
                    raise ValueError(
                        f"No existe daily_summary para {date_value}"
                    )

                # Guardar resultado de cada target
                for target in targets:

                    model_result = build_daily_model_result(
                        y_true=daily_df[target],
                        y_pred=daily_df[f"pred_{target}"],
                        model_id=model_ids_by_target[target],
                        model_name=model_name,
                        target=target,
                        dataset_version=dataset_version,
                        n_features=len(features),
                        train_year=train_year,
                        test_year=test_year
                    )

                    upsert_daily_model_result(
                        collection=collection,
                        document_filter=document_filter,
                        model_result=model_result
                    )

                success.append(str(date_value))

            except Exception as exc:

                errors.append({
                    "fecha": str(date_value),
                    "error": str(exc)
                })

        print(
            f"Días procesados correctamente: {len(success)}"
        )

        print(
            f"Días con error: {len(errors)}"
        )

        return {
            "success": success,
            "errors": pd.DataFrame(errors)
        }

    finally:
        client.close()