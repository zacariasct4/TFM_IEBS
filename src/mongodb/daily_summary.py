from datetime import datetime, timezone

import pandas as pd
import numpy as np


def to_python_number(value):
    """
    Convierte valores NumPy o pandas a tipos nativos de Python.
    """

    if pd.isna(value):
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    return value

def numeric_summary(series: pd.Series) -> dict:
    """
    Calcula las principales estadísticas descriptivas de una serie.
    """

    valid_values = series.dropna()

    if valid_values.empty:
        return {
            "media": None,
            "mediana": None,
            "minimo": None,
            "maximo": None,
            "desviacion_estandar": None,
            "nulos": int(series.isna().sum()),
        }

    return {
        "media": to_python_number(valid_values.mean()),
        "mediana": to_python_number(valid_values.median()),
        "minimo": to_python_number(valid_values.min()),
        "maximo": to_python_number(valid_values.max()),
        "desviacion_estandar": to_python_number(valid_values.std()),
        "nulos": int(series.isna().sum()),
    }

def categorical_distribution(series: pd.Series) -> dict:
    """
    Calcula la distribución absoluta y porcentual de una variable categórica.
    """

    counts = series.value_counts(dropna=False).sort_index()
    total = len(series)

    absolute = {}
    percentage = {}

    for category, count in counts.items():
        category_key = "null" if pd.isna(category) else str(category)

        absolute[category_key] = int(count)
        percentage[category_key] = round(
            float(count / total * 100),
            4,
        )

    return {
        "frecuencia": absolute,
        "porcentaje": percentage,
    }

def binary_summary(series: pd.Series) -> dict:
    """
    Resume una variable indicadora binaria.

    El valor 0 representa la ausencia de la condición y el valor 1
    representa su presencia.
    """

    numeric_series = pd.to_numeric(
        series,
        errors="coerce",
    )

    invalid_values = numeric_series[
        numeric_series.notna()
        & ~numeric_series.isin([0, 1])
    ]

    if not invalid_values.empty:
        raise ValueError(
            "La serie contiene valores distintos de 0 y 1."
        )

    total = len(numeric_series)
    positives = int(numeric_series.eq(1).sum())
    negatives = int(numeric_series.eq(0).sum())
    nulls = int(numeric_series.isna().sum())

    valid_total = positives + negatives

    percentage = (
        round(positives / valid_total * 100, 4)
        if valid_total > 0
        else None
    )

    return {
        "valor_0": negatives,
        "valor_1": positives,
        "nulos": nulls,
        "porcentaje_valor_1": percentage,
    }

def build_processing_summary(df: pd.DataFrame) -> dict:
    """
    Resume los indicadores de imputación meteorológica y ausencia
    original de irradiancias.
    """

    return {
        "imputacion_meteorologica": {
            "descripcion": (
                "Indica si al menos una variable meteorológica "
                "del registro ha sido imputada."
            ),
            **binary_summary(df["var_meteo_imp"]),
        },
        "irradiancia_original_nula": {
            "descripcion": (
                "Indica si el registro presentaba al menos una "
                "irradiancia nula antes del tratamiento."
            ),
            **binary_summary(df["irr_null"]),
        },
    }

def build_quality_summary(df: pd.DataFrame) -> dict:
    """
    Construye la distribución diaria de los códigos de calidad
    de GHI, DNI y DHI.
    """

    return {
        "codigo_ghi": categorical_distribution(
            df["codigo_ghi"]
        ),
        "codigo_dni": categorical_distribution(
            df["codigo_dni"]
        ),
        "codigo_dhi": categorical_distribution(
            df["codigo_dhi"]
        ),
    }


def build_daily_document(
    df: pd.DataFrame,
    dataset_version: str = "v3",
) -> dict:
    """
    Construye un documento de resumen diario compatible con MongoDB.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame correspondiente exclusivamente a un día.
    dataset_version : str
        Versión del dataset utilizada.

    Returns
    -------
    dict
        Documento diario preparado para su posterior inserción
        en MongoDB.
    """

    if df.empty:
        raise ValueError(
            "No se puede construir un documento a partir "
            "de un DataFrame vacío."
        )

    df = df.copy()

    # Las fechas almacenadas proceden originalmente de una serie UTC.
    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce",
    )

    if df["fecha"].isna().any():
        raise ValueError(
            "Existen valores de fecha que no se han podido convertir."
        )

    unique_dates = df["fecha"].dt.date.unique()

    if len(unique_dates) != 1:
        raise ValueError(
            "El DataFrame contiene registros correspondientes "
            "a más de un día."
        )

    document_date = pd.Timestamp(unique_dates[0])

    registros_dia = int(
        df["periodo_solar"].eq("dia").sum()
    )

    registros_noche = int(
        df["periodo_solar"].eq("noche").sum()
    )

    now_utc = datetime.now(timezone.utc)

    daily_document = {
        "fecha": datetime(
            year=document_date.year,
            month=document_date.month,
            day=document_date.day,
            tzinfo=timezone.utc,
        ),

        "dataset": {
            "version": dataset_version,
            "origen": "PostgreSQL",
            "tabla_origen": "solar.measurements",
        },

        "periodo": {
            "ano": int(document_date.year),
            "mes": int(document_date.month),
            "dia": int(document_date.day),
            "dia_semana": int(document_date.dayofweek),
        },

        "cobertura": {
            "numero_registros": int(len(df)),
            "fecha_inicio": df["fecha"].min().to_pydatetime(),
            "fecha_fin": df["fecha"].max().to_pydatetime(),
            "fechas_duplicadas": int(
                df["fecha"].duplicated().sum()
            ),
            "periodo_solar": {
                "registros_dia": registros_dia,
                "registros_noche": registros_noche,
            },
        },

        "irradiancia": {
            "ghi": numeric_summary(df["ghi"]),
            "dni": numeric_summary(df["dni"]),
            "dhi": numeric_summary(df["dhi"]),
            "ghi_estimado": numeric_summary(
                df["ghi_estimado"]
            ),
        },

        "meteorologia": {
            "temperatura": numeric_summary(
                df["temperatura"]
            ),
            "humedad_relativa": numeric_summary(
                df["humedad_relativa"]
            ),
            "velocidad_viento": numeric_summary(
                df["velocidad_viento"]
            ),
            "direccion_viento": numeric_summary(
                np.degrees(np.arctan2(
                    df["direccion_viento_sin"], df["direccion_viento_cos"]
                    )) % 360
            )
        },

        "variables_fisicas": {
            "elevacion_solar": numeric_summary(
                df["elevacion_solar"]
            ),
            "error_balance": numeric_summary(
                df["error_balance"]
            ),
            "error_balance_abs": numeric_summary(
                df["error_balance_abs"]
            ),
            "error_balance_rel": numeric_summary(
                df["error_balance_rel"]
            ),
        },

        "calidad": build_quality_summary(df),

        "procesamiento": build_processing_summary(df),

        "graficas": {
            "curvas_solares": {
                "disponible": False,
                "ruta": None,
                "formato": None,
                "fecha_generacion": None,
            },
            "calidad_meteorologia": {
                "disponible": False,
                "ruta": None,
                "formato": None,
                "fecha_generacion": None,
            },
        },

        "resultados_modelos": {
            "disponible": False,
            "ejecuciones": [],
        },

        "anomalias_modelo": {
            "disponible": False,
            "eventos": [],
        },

        "explicacion_automatica": {
            "disponible": False,
            "texto": None,
            "modelo_generador": None,
            "fecha_generacion": None,
        },

        "metadatos": {
            "schema_version": "1.0",
            "created_at": now_utc,
            "updated_at": now_utc,
        },
    }

    return daily_document