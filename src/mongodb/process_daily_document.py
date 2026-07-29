"""Procesamiento completo de un documento diario para MongoDB."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from pymongo.collection import Collection
from sqlalchemy.engine import Engine

from src.database.load_daily_measurements import load_daily_measurements
from src.mongodb.daily_plots import (
    generate_quality_weather_plot,
    generate_solar_curves_plot,
)
from src.mongodb.daily_summary import build_daily_document
from src.mongodb.load_documents import upsert_daily_document


def process_daily_document(
    date: str,
    postgres_engine: Engine,
    mongodb_collection: Collection,
    output_directory: Path,
    dataset_version: str = "v3",
) -> Dict[str, Any]:
    """
    Procesa una fecha completa y almacena su documento en MongoDB.

    El flujo incluye:

    1. carga de las mediciones desde PostgreSQL;
    2. preparación de las fechas;
    3. construcción del documento diario;
    4. generación de las gráficas;
    5. incorporación de sus metadatos;
    6. inserción o actualización mediante `upsert`.

    Parameters
    ----------
    date : str
        Fecha que se desea procesar en formato `YYYY-MM-DD`.
    postgres_engine : Engine
        Motor de conexión con PostgreSQL.
    mongodb_collection : Collection
        Colección de MongoDB en la que se almacenará el documento.
    output_directory : Path
        Directorio base en el que se guardarán las gráficas.
    dataset_version : str
        Versión del dataset utilizada para construir el documento.

    Returns
    -------
    dict
        Resumen del resultado del procesamiento.

    Raises
    ------
    ValueError
        Si las fechas no pueden convertirse correctamente.
    FileNotFoundError
        Si alguna de las gráficas no se genera correctamente.
    """

    # Recupera desde PostgreSQL todas las mediciones del día.
    df_day = load_daily_measurements(
        engine=postgres_engine,
        date=date,
    )

    df_day = df_day.copy()

    # Convierte la fecha al tipo datetime utilizado en las gráficas.
    df_day["fecha"] = pd.to_datetime(
        df_day["fecha"],
        errors="coerce",
    )

    if df_day["fecha"].isna().any():
        raise ValueError(
            f"Existen fechas inválidas en los datos del día {date}."
        )

    # Columna auxiliar utilizada por las funciones de representación.
    df_day["hora_local"] = df_day["fecha"]

    # Construye el documento de resumen diario.
    daily_document = build_daily_document(
        df=df_day,
        dataset_version=dataset_version,
    )

    # Genera las dos gráficas asociadas al día.
    solar_curves_path = generate_solar_curves_plot(
        df=df_day,
        output_directory=output_directory,
    )

    quality_weather_path = generate_quality_weather_plot(
        df=df_day,
        output_directory=output_directory,
    )

    generated_paths = {
        "curvas_solares": solar_curves_path,
        "calidad_meteorologia": quality_weather_path,
    }

    # Comprueba que las imágenes se han generado correctamente.
    for plot_name, plot_path in generated_paths.items():
        if not plot_path.exists():
            raise FileNotFoundError(
                f"No se ha generado la gráfica "
                f"'{plot_name}' para la fecha {date}."
            )

        if plot_path.stat().st_size == 0:
            raise ValueError(
                f"La gráfica '{plot_name}' del día {date} está vacía."
            )

    generation_time = datetime.now(timezone.utc)

    # Añade las rutas y metadatos de las imágenes al documento.
    daily_document["graficas"] = {
        "curvas_solares": {
            "disponible": True,
            "ruta": solar_curves_path.as_posix(),
            "formato": "png",
            "fecha_generacion": generation_time,
        },
        "calidad_meteorologia": {
            "disponible": True,
            "ruta": quality_weather_path.as_posix(),
            "formato": "png",
            "fecha_generacion": generation_time,
        },
    }

    daily_document["metadatos"]["updated_at"] = generation_time

    # Inserta o actualiza el documento en MongoDB.
    result = upsert_daily_document(
        collection=mongodb_collection,
        document=daily_document,
    )

    return {
        "fecha": date,
        "registros": len(df_day),
        "insertado": result.upserted_id is not None,
        "actualizado": result.modified_count > 0,
        "upserted_id": (
            str(result.upserted_id)
            if result.upserted_id is not None
            else None
        ),
        "ruta_curvas_solares": solar_curves_path.as_posix(),
        "ruta_calidad_meteorologia": quality_weather_path.as_posix(),
    }