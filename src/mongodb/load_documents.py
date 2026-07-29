"""Funciones para crear índices y cargar documentos diarios en MongoDB."""

from __future__ import annotations

from typing import Any, Dict

from pymongo.collection import Collection
from pymongo.results import UpdateResult


def create_daily_documents_index(collection: Collection) -> str:
    """
    Crea el índice único utilizado para identificar cada documento diario.

    La combinación de la fecha y la versión del dataset permite conservar
    documentos correspondientes al mismo día cuando proceden de versiones
    diferentes del conjunto de datos.

    Parameters
    ----------
    collection : Collection
        Colección de MongoDB que contiene los documentos diarios.

    Returns
    -------
    str
        Nombre del índice creado o del índice ya existente.
    """

    return collection.create_index(
        [
            ("fecha", 1),
            ("dataset.version", 1),
        ],
        unique=True,
        name="uq_daily_document_date_dataset_version",
    )


def upsert_daily_document(
    collection: Collection,
    document: Dict[str, Any],
) -> UpdateResult:
    """
    Inserta o actualiza un documento diario sin generar duplicados.

    Si ya existe un documento con la misma fecha y versión del dataset,
    su contenido se actualiza. En caso contrario, se crea un nuevo documento.

    Parameters
    ----------
    collection : Collection
        Colección de MongoDB en la que se almacenará el documento.
    document : dict
        Documento diario generado por `build_daily_document`.

    Returns
    -------
    UpdateResult
        Resultado devuelto por MongoDB después de la operación `upsert`.

    Raises
    ------
    ValueError
        Si el documento no contiene los campos necesarios para identificarlo.
    """

    # La fecha es necesaria para identificar el día representado.
    if "fecha" not in document:
        raise ValueError(
            "El documento no contiene el campo obligatorio 'fecha'."
        )

    dataset = document.get("dataset")

    # La versión del dataset permite diferenciar documentos de distintas
    # versiones para una misma fecha.
    if not isinstance(dataset, dict) or not dataset.get("version"):
        raise ValueError(
            "El documento no contiene el campo obligatorio "
            "'dataset.version'."
        )

    # Filtro utilizado para localizar de forma unívoca el documento.
    document_filter = {
        "fecha": document["fecha"],
        "dataset.version": dataset["version"],
    }

    # `upsert=True` actualiza el documento si existe y lo crea si no existe.
    return collection.update_one(
        document_filter,
        {"$set": document},
        upsert=True,
    )