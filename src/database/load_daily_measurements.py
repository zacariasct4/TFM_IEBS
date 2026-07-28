import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def load_daily_measurements(
    engine: Engine,
    date: str,
    schema: str = "solar",
    table: str = "measurements",
) -> pd.DataFrame:
    """
    Recupera las mediciones correspondientes a una fecha concreta.
    """

    query = text(
        f"""
        SELECT *
        FROM {schema}.{table}
        WHERE fecha >= CAST(:target_date AS DATE)
          AND fecha < CAST(:target_date AS DATE) + INTERVAL '1 day'
        ORDER BY fecha;
        """
    )

    df_day = pd.read_sql_query(
        query,
        con=engine,
        params={"target_date": date},
    )

    if df_day.empty:
        raise ValueError(
            f"No se han encontrado registros para la fecha {date}."
        )

    return df_day