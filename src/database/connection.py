import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


load_dotenv()


def get_database_engine() -> Engine:
    """Crea y devuelve un SQLAlchemy engine para PostgreSQL."""

    required_variables = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise EnvironmentError(
            f"Missing environment variables: {missing_variables}"
        )

    database_url = (
        f"postgresql+psycopg://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def test_database_connection() -> dict:
    """Testea la conexión PostgreSQL y devuelve información básica."""

    engine = get_database_engine()

    query = text(
        """
        SELECT
            current_database() AS database_name,
            current_user AS user_name,
            current_schema() AS schema_name;
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query).mappings().one()

    return dict(result)


if __name__ == "__main__":
    connection_info = test_database_connection()
    print("PostgreSQL connection successful:")
    print(connection_info)