"""Funciones para obtener las fechas disponibles en PostgreSQL."""

from __future__ import annotations

from typing import List

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def load_available_dates(
    engine: Engine,
    schema: str = "solar",
    table: str = "measurements",
) -> List[str]:
    """
    Recupera las fechas disponibles en la tabla de mediciones.

    La función consulta las fechas realmente existentes en PostgreSQL,
    evitando construir manualmente un rango que podría incluir días sin datos.

    Parameters
    ----------
    engine : Engine
        Motor de conexión con PostgreSQL.
    schema : str
        Esquema en el que se encuentra la tabla.
    table : str
        Tabla que contiene las mediciones.

    Returns
    -------
    list of str
        Lista ordenada de fechas en formato `YYYY-MM-DD`.

    Raises
    ------
    ValueError
        Si la consulta no devuelve ninguna fecha.
    """

    query = text(
        f"""
        SELECT DISTINCT fecha::date AS fecha
        FROM {schema}.{table}
        ORDER BY fecha;
        """
    )

    dates_df = pd.read_sql_query(
        query,
        con=engine,
    )

    if dates_df.empty:
        raise ValueError(
            "No se han encontrado fechas disponibles en PostgreSQL."
        )

    available_dates = (
        pd.to_datetime(
            dates_df["fecha"],
            errors="coerce",
        )
        .dropna()
        .dt.strftime("%Y-%m-%d")
        .tolist()
    )

    if not available_dates:
        raise ValueError(
            "Las fechas recuperadas no se han podido convertir correctamente."
        )

    return available_dates