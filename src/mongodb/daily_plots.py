from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def generate_solar_curves_plot(
    df: pd.DataFrame,
    output_directory: Path,
) -> Path:
    """
    Genera una gráfica diaria de las curvas de irradiancia solar.

    Parameters
    ----------
    df : pd.DataFrame
        Datos correspondientes a un único día.
    output_directory : Path
        Directorio en el que se guardará la imagen.

    Returns
    -------
    Path
        Ruta del archivo generado.
    """

    if df.empty:
        raise ValueError(
            "No se puede generar una gráfica con un DataFrame vacío."
        )

    required_columns = [
        "hora_local",
        "ghi",
        "dni",
        "dhi",
        "ghi_estimado",
        "elevacion_solar",
        "codigo_ghi",
        "codigo_dni",
        "codigo_dhi",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Faltan columnas necesarias para la gráfica: "
            + ", ".join(missing_columns)
        )

    plot_date = df["fecha"].dt.date.iloc[0]

    output_path = (
        output_directory
        / f"{plot_date}_solar_curves.png"
    )

    fig, ax_irradiance = plt.subplots(
        figsize=(15, 7)
    )

    ax_irradiance.plot(
        df["hora_local"],
        df["ghi"],
        label="GHI",
        linewidth=1.2,
    )

    ax_irradiance.plot(
        df["hora_local"],
        df["dni"],
        label="DNI",
        linewidth=1.2,
    )

    ax_irradiance.plot(
        df["hora_local"],
        df["dhi"],
        label="DHI",
        linewidth=1.2,
    )

    ax_irradiance.plot(
        df["hora_local"],
        df["ghi_estimado"],
        label="GHI estimado",
        linewidth=1,
        linestyle="--",
    )

    incorrect_mask = (
        df[
            [
                "codigo_ghi",
                "codigo_dni",
                "codigo_dhi",
            ]
        ]
        .eq(1)
        .any(axis=1)
    )

    ax_irradiance.scatter(
        df.loc[incorrect_mask, "hora_local"],
        df.loc[incorrect_mask, "ghi"],
        label="Medición incorrecta",
        s=12,
        zorder=3,
    )

    ax_irradiance.set_title(
        f"Curvas solares diarias — {plot_date}"
    )

    ax_irradiance.set_xlabel("Hora local")
    ax_irradiance.set_ylabel("Irradiancia (W/m²)")
    ax_irradiance.grid(alpha=0.3)

    ax_elevation = ax_irradiance.twinx()

    ax_elevation.plot(
        df["hora_local"],
        df["elevacion_solar"],
        label="Elevación solar",
        linewidth=1,
        alpha=0.6,
    )

    ax_elevation.set_ylabel("Elevación solar (°)")

    handles_1, labels_1 = (
        ax_irradiance.get_legend_handles_labels()
    )

    handles_2, labels_2 = (
        ax_elevation.get_legend_handles_labels()
    )

    ax_irradiance.legend(
        handles_1 + handles_2,
        labels_1 + labels_2,
        loc="upper left",
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output_path

def generate_quality_weather_plot(
    df: pd.DataFrame,
    output_directory: Path,
) -> Path:
    """
    Genera una gráfica diaria con códigos de calidad,
    variables meteorológicas e indicadores de procesamiento.
    """

    if df.empty:
        raise ValueError(
            "No se puede generar una gráfica con un DataFrame vacío."
        )

    required_columns = [
        "hora_local",
        "temperatura",
        "humedad_relativa",
        "velocidad_viento",
        "codigo_ghi",
        "codigo_dni",
        "codigo_dhi",
        "var_meteo_imp",
        "irr_null",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Faltan columnas necesarias para la gráfica: "
            + ", ".join(missing_columns)
        )

    plot_date = df["fecha"].dt.date.iloc[0]

    output_path = (
        output_directory
        / f"{plot_date}_quality_weather.png"
    )

    fig, axes = plt.subplots(
        nrows=3,
        ncols=1,
        figsize=(15, 11),
        sharex=True,
    )

    axes[0].plot(
        df["hora_local"],
        df["temperatura"],
        label="Temperatura",
    )

    axes[0].plot(
        df["hora_local"],
        df["humedad_relativa"],
        label="Humedad relativa",
    )

    axes[0].plot(
        df["hora_local"],
        df["velocidad_viento"],
        label="Velocidad del viento",
    )

    axes[0].set_ylabel("Variables meteorológicas")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].step(
        df["hora_local"],
        df["codigo_ghi"],
        label="Código GHI",
        where="post",
    )

    axes[1].step(
        df["hora_local"],
        df["codigo_dni"],
        label="Código DNI",
        where="post",
    )

    axes[1].step(
        df["hora_local"],
        df["codigo_dhi"],
        label="Código DHI",
        where="post",
    )

    axes[1].set_ylabel("Código de calidad")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    axes[2].step(
        df["hora_local"],
        df["var_meteo_imp"],
        label="Variable meteorológica imputada",
        where="post",
    )

    axes[2].step(
        df["hora_local"],
        df["irr_null"],
        label="Irradiancia originalmente nula",
        where="post",
    )

    axes[2].set_ylabel("Indicador binario")
    axes[2].set_xlabel("Hora local")
    axes[2].legend()
    axes[2].grid(alpha=0.3)

    fig.suptitle(
        f"Calidad, meteorología y procesamiento — {plot_date}"
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output_path