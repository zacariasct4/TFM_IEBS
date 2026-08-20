import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    f1_score,
    balanced_accuracy_score,
    ConfusionMatrixDisplay
)


def evaluate_predictions(
    y_true,
    y_pred,
    model_name,
    target,
    n_features
):
    """
    Calcula las métricas principales de evaluación para un target.

    Se utiliza Macro F1 como métrica decisoria y Balanced Accuracy
    y Weighted F1 como métricas complementarias.

    Parameters
    ----------
    y_true : array-like
        Valores reales del target.
    y_pred : array-like
        Predicciones realizadas por el modelo.
    model_name : str
        Nombre del modelo evaluado.
    target : str
        Nombre de la variable objetivo.
    n_features : int
        Número de variables utilizadas por el modelo.

    Returns
    -------
    dict
        Diccionario con identificación del modelo y sus métricas.
    """

    return {
        "model": model_name,
        "target": target,
        "n_features": n_features,
        "f1_macro": f1_score(
            y_true,
            y_pred,
            average="macro",
            zero_division=0
        ),
        "balanced_accuracy": balanced_accuracy_score(
            y_true,
            y_pred
        ),
        "f1_weighted": f1_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0
        )
    }


def evaluate_model_predictions(
    test_df,
    predictions,
    targets,
    model_name,
    features
):
    """
    Evalúa un mismo modelo para todos los targets del proyecto.

    La función utiliza las predicciones previamente generadas y devuelve
    una fila de resultados por cada código de calidad.

    Parameters
    ----------
    test_df : pd.DataFrame
        Dataset de test con los valores reales.
    predictions : dict
        Diccionario con una predicción por target.
    targets : list
        Lista de variables objetivo.
    model_name : str
        Nombre del modelo.
    features : list
        Variables utilizadas durante el entrenamiento.

    Returns
    -------
    pd.DataFrame
        Tabla con las métricas para cada target.
    """

    results = []

    for target in targets:

        metrics = evaluate_predictions(
            y_true=test_df[target],
            y_pred=predictions[target],
            model_name=model_name,
            target=target,
            n_features=len(features)
        )

        results.append(metrics)

    return pd.DataFrame(results)


def plot_confusion_matrices(
    test_df,
    predictions,
    targets,
    model_name
):
    """
    Representa las matrices de confusión de todos los targets
    en una única fila.

    Permite observar directamente qué clases son confundidas
    por el modelo y complementa las métricas agregadas.
    """

    fig, axes = plt.subplots(
        1,
        len(targets),
        figsize=(5 * len(targets), 4)
    )

    axes = np.atleast_1d(axes)

    for ax, target in zip(axes, targets):

        ConfusionMatrixDisplay.from_predictions(
            test_df[target],
            predictions[target],
            ax=ax,
            colorbar=False
        )

        ax.set_title(
            target.replace("codigo_", "").upper()
        )

    fig.suptitle(
        f"Matrices de confusión - {model_name}",
        fontsize=14
    )

    plt.tight_layout()
    plt.show()


def plot_correct_predictions_by_class(
    test_df,
    predictions,
    targets,
    model_name
):
    """
    Representa, para cada target y para cada clase real,
    el número de observaciones correctamente e incorrectamente
    clasificadas.

    Esta visualización permite detectar rápidamente si el modelo
    funciona bien sobre las clases mayoritarias pero presenta
    dificultades con las clases minoritarias.
    """

    for target in targets:

        y_true = test_df[target].to_numpy()
        y_pred = np.asarray(predictions[target])

        classes = np.sort(np.unique(y_true))

        class_results = []

        for cls in classes:

            class_mask = y_true == cls

            total = class_mask.sum()

            correct = (
                (y_true == cls) &
                (y_pred == cls)
            ).sum()

            incorrect = total - correct

            class_results.append({
                "class": cls,
                "correct": correct,
                "incorrect": incorrect
            })

        class_results = pd.DataFrame(class_results)

        x = np.arange(len(class_results))
        width = 0.35

        fig, ax = plt.subplots(
            figsize=(7, 4)
        )

        ax.bar(
            x - width / 2,
            class_results["correct"],
            width,
            label="Correctos"
        )

        ax.bar(
            x + width / 2,
            class_results["incorrect"],
            width,
            label="Incorrectos"
        )

        ax.set_xticks(x)
        ax.set_xticklabels(
            class_results["class"]
        )

        ax.set_xlabel("Código real")
        ax.set_ylabel("Número de observaciones")

        ax.set_title(
            f"{model_name} - {target}"
        )

        ax.legend()

        plt.tight_layout()
        plt.show()


def create_model_comparison_table(
    results_df
):
    """
    Genera una tabla compacta para comparar rápidamente los modelos.

    Cada fila representa un modelo y número de features, mientras que
    las columnas muestran el Macro F1 obtenido para GHI, DNI y DHI.

    Parameters
    ----------
    results_df : pd.DataFrame
        Tabla acumulada con los resultados de todos los modelos.

    Returns
    -------
    pd.DataFrame
        Tabla comparativa en formato pivot.
    """

    comparison = (
        results_df
        .pivot_table(
            index=[
                "model",
                "n_features"
            ],
            columns="target",
            values="f1_macro"
        )
        .reset_index()
    )

    comparison.columns.name = None

    target_order = [
        "codigo_ghi",
        "codigo_dni",
        "codigo_dhi"
    ]

    existing_targets = [
        target
        for target in target_order
        if target in comparison.columns
    ]

    comparison = comparison[
        ["model", "n_features"]
        + existing_targets
    ]

    return comparison