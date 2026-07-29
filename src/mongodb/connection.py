"""Utilidades de conexión con MongoDB para el proyecto de irradiancia solar."""

from __future__ import annotations

import os
from typing import Tuple

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.server_api import ServerApi


def get_mongodb_database() -> Tuple[Database, MongoClient]:
    """
    Crea y valida una conexión con MongoDB Atlas.

    La función carga las credenciales desde el archivo `.env`, crea el
    cliente de MongoDB, comprueba la conexión mediante una operación `ping`
    y devuelve tanto la base de datos seleccionada como el cliente.

    Returns
    -------
    tuple
        Objeto de la base de datos de MongoDB y cliente MongoDB asociado.

    Raises
    ------
    ValueError
        Si faltan variables de entorno obligatorias.
    ConnectionError
        Si no se puede establecer la conexión con MongoDB Atlas.
    """
    load_dotenv()

    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_database = os.getenv("MONGODB_DATABASE")

    # Comprueba que estén disponibles todas las variables necesarias.
    missing_variables = [
        variable_name
        for variable_name, variable_value in {
            "MONGODB_URI": mongodb_uri,
            "MONGODB_DATABASE": mongodb_database,
        }.items()
        if not variable_value
    ]

    if missing_variables:
        raise ValueError(
            "Faltan las siguientes variables en el archivo .env: "
            + ", ".join(missing_variables)
        )

    # Crea el cliente utilizando la Stable API de MongoDB.
    client = MongoClient(
        mongodb_uri,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10_000,
    )

    # Verifica que el clúster está accesible y las credenciales son válidas.
    try:
        client.admin.command("ping")
    except Exception as exc:
        client.close()
        raise ConnectionError(
            "No se ha podido establecer la conexión con MongoDB Atlas."
        ) from exc

    # Selecciona la base de datos configurada en el archivo .env.
    database = client[mongodb_database]

    return database, client