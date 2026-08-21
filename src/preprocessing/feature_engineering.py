import numpy as np

def encode_cyclic_features(df):
    """
    La función codifica la dirección del viento, la hora del día y el mes
    del año mediante transformaciones trigonométricas. Esto permite representar
    correctamente su carácter periódico, de forma que valores cercanos al inicio
    y al final de cada ciclo también queden próximos en el espacio transformado.
    """
    df = df.copy()
    df['direccion_viento_sin'] = np.sin(np.radians(df['direccion_viento']))
    df['direccion_viento_cos'] = np.cos(np.radians(df['direccion_viento']))

    df["hora_sin"] = np.sin(2 * np.pi * df["hora"] / 24)
    df["hora_cos"] = np.cos(2 * np.pi * df["hora"] / 24)

    df["mes_sin"] = np.sin(2 * np.pi * (df["mes"] - 1) / 12)
    df["mes_cos"] = np.cos(2 * np.pi * (df["mes"] - 1) / 12)

    df = df.drop(columns=["direccion_viento", "hora", "mes"])
    ordered_columns = ['ano', 'mes_sin', 'mes_cos', 'dia', 'hora_sin', 'hora_cos', 'minuto', 'fecha', 'ghi', 'dni', 'dhi',
       'temperatura', 'velocidad_viento', 'humedad_relativa', 'direccion_viento_sin', 'direccion_viento_cos',
        'codigo_ghi', 'codigo_dni', 'codigo_dhi']
    df = df[ordered_columns]

    return df