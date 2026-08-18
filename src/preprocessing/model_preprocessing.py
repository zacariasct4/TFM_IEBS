import pandas as pd

from sklearn.preprocessing import StandardScaler


METEO_FEATURES = [
    "temperatura",
    "velocidad_viento",
    "humedad_relativa",
    "direccion_viento_sin",
    "direccion_viento_cos",
]

IRRADIANCE_FEATURES = [
    "ghi",
    "dni",
    "dhi",
]

BALANCE_FEATURES = [
    "error_balance_abs",
]

MISSING_INDICATOR = "irr_null"


def prepare_model_features(
    train_df,
    test_df,
    features,
    accepts_nan,
    scale=False,
):
    """
    Prepara las variables predictoras según las necesidades del modelo.

    Parameters
    ----------
    train_df : pd.DataFrame
        Dataset de entrenamiento.

    test_df : pd.DataFrame
        Dataset de test.

    features : list
        Variables candidatas seleccionadas previamente.

    accepts_nan : bool
        Indica si el modelo admite valores NaN de forma nativa.

    scale : bool, default=False
        Si True, estandariza las variables utilizando únicamente
        los parámetros aprendidos sobre train.

    Returns
    -------
    X_train : pd.DataFrame
        Variables de entrenamiento preparadas.

    X_test : pd.DataFrame
        Variables de test preparadas.

    used_features : list
        Variables finalmente utilizadas.

    scaler : StandardScaler or None
        Scaler ajustado sobre train cuando scale=True.
    """

    used_features = features.copy()

    if accepts_nan:

        # Los propios NaN ya indican ausencia de dato.
        if MISSING_INDICATOR in used_features:
            used_features.remove(MISSING_INDICATOR)

    else:

        # Las variables meteorológicas con NaN no se utilizan.
        used_features = [
            feature
            for feature in used_features
            if feature not in METEO_FEATURES
        ]

    X_train = train_df[used_features].copy()
    X_test = test_df[used_features].copy()

    if not accepts_nan:

        features_to_fill = [
            feature
            for feature in IRRADIANCE_FEATURES + BALANCE_FEATURES
            if feature in used_features
        ]

        X_train[features_to_fill] = (
            X_train[features_to_fill]
            .fillna(0)
        )

        X_test[features_to_fill] = (
            X_test[features_to_fill]
            .fillna(0)
        )

        if X_train.isna().any().any():
            missing_cols = X_train.columns[
                X_train.isna().any()
            ].tolist()

            raise ValueError(
                f"Quedan NaN en train: {missing_cols}"
            )

        if X_test.isna().any().any():
            missing_cols = X_test.columns[
                X_test.isna().any()
            ].tolist()

            raise ValueError(
                f"Quedan NaN en test: {missing_cols}"
            )

    scaler = None

    if scale:

        scaler = StandardScaler()

        X_train = pd.DataFrame(
            scaler.fit_transform(X_train),
            columns=used_features,
            index=X_train.index,
        )

        X_test = pd.DataFrame(
            scaler.transform(X_test),
            columns=used_features,
            index=X_test.index,
        )

    return (
        X_train,
        X_test,
        used_features,
        scaler,
    )