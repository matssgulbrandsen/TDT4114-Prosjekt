from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import ipywidgets as widgets
from IPython.display import display

def plot_sammenligning_miljodata(
    project_root=None
):
    """
    Interaktivt plotter som sammenligner årlig gjennomsnittlig temperatur, havnivå og albedo-effekt (1992–2025),
    med av/på-knapper for hver dataserie og tilhørende regresjonslinjer.

    """

    # Finn projekt roten
    if project_root is None:
        project_root = Path(__file__).resolve().parents[2]

    # Temperaturdata
    temp_path = project_root / "data" / "temperaturdata" / "temperaturdata.csv"
    df_temp = pd.read_csv(temp_path)
    df_temp["date"] = pd.to_datetime(df_temp["date"])
    df_temp["år"] = df_temp["date"].dt.year
    temp_aar = df_temp.groupby("år")["temperature_2m"].mean().reset_index()
    temp_aar.rename(columns={"temperature_2m": "Temperatur (gjennomsnitt)"}, inplace=True)

    # Havnivådata
    havniva_path = project_root / "data" / "Havnivådata" / "havnivaadata.json"
    df_havniv = pd.read_json(havniva_path, lines=True)
    df_havniv["iso_time"] = pd.to_datetime(df_havniv["iso_time"])
    df_havniv["år"] = df_havniv["iso_time"].dt.year
    df_havniv["mean_mm"] = df_havniv["mean"] * 1000
    hav_aar = df_havniv.groupby("år")["mean_mm"].mean().reset_index()
    hav_aar.rename(columns={"mean_mm": "Havnivå (gjennomsnitt)"}, inplace=True)

    # Albedo effekt data
    sys.path.append(str(project_root / "src"))  # For å finne src-pakker
    from albedo_effekt.datavisualisering import Visualisering
    from albedo_effekt.dataanalyse import albedo_statistikk_faste_2004_punkter

    v = Visualisering()
    albedo_matrise, årstall, gjennomsnitt, median, std = albedo_statistikk_faste_2004_punkter(print_matrise=False)
    albedo_aar = pd.DataFrame({
        "år": årstall,
        "Albedo (gjennomsnitt)": gjennomsnitt
    })

    # Sikre likt intervall 1992-2025, kun felles år
    start_aar, slutt_aar = 1992, 2025
    for df in [temp_aar, hav_aar, albedo_aar]:
        df.drop(df[(df["år"] < start_aar) | (df["år"] > slutt_aar)].index, inplace=True)

    # Flett sammen de tre dataseriene (temperatur, havnivå og albedo) på årstall
    df_sammen = temp_aar.merge(hav_aar, on="år", how="inner").merge(albedo_aar, on="år", how="inner").sort_values("år")

    # Widgets for av/på knapper
    cb_temp = widgets.Checkbox(value=True, description="Temperatur")
    cb_havniva = widgets.Checkbox(value=True, description="Havnivå")
    cb_albedo = widgets.Checkbox(value=True, description="Albedo")
    cb_reg_temp = widgets.Checkbox(value=False, description="Regresjon temperatur")
    cb_reg_havniva = widgets.Checkbox(value=False, description="Regresjon havnivå")
    cb_reg_albedo = widgets.Checkbox(value=False, description="Regresjon albedo")
    output = widgets.Output()

    def plot_oppdater(*args):
        output.clear_output()
        with output:
            fig = go.Figure()
            # Temperatur
            if cb_temp.value:
                fig.add_trace(go.Scatter(
                    x=df_sammen["år"], y=df_sammen["Temperatur (gjennomsnitt)"],
                    name="Temperatur (gjennomsnitt)", mode="lines+markers", yaxis="y1", line=dict(color="red")))
            if cb_reg_temp.value:
                mask = ~np.isnan(df_sammen["Temperatur (gjennomsnitt)"])
                x = df_sammen.loc[mask, "år"]
                y = df_sammen.loc[mask, "Temperatur (gjennomsnitt)"]
                if len(x) > 1:
                    z = np.polyfit(x, y, 1)
                    trend = np.polyval(z, x)
                    fig.add_trace(go.Scatter(
                        x=x, y=trend,
                        mode="lines",
                        name="Regresjon temperatur",
                        line=dict(width=2, dash="dot", color="darkred"),
                        yaxis="y1"
                    ))
            # Havnivå
            if cb_havniva.value:
                fig.add_trace(go.Scatter(
                    x=df_sammen["år"], y=df_sammen["Havnivå (gjennomsnitt)"],
                    name="Havnivå (gjennomsnitt)", mode="lines+markers", yaxis="y2", line=dict(color="blue")))
            if cb_reg_havniva.value:
                mask = ~np.isnan(df_sammen["Havnivå (gjennomsnitt)"])
                x = df_sammen.loc[mask, "år"]
                y = df_sammen.loc[mask, "Havnivå (gjennomsnitt)"]
                if len(x) > 1:
                    z = np.polyfit(x, y, 1)
                    trend = np.polyval(z, x)
                    fig.add_trace(go.Scatter(
                        x=x, y=trend,
                        mode="lines",
                        name="Regresjon havnivå",
                        line=dict(width=2, dash="dot", color="darkblue"),
                        yaxis="y2"
                    ))
            # Albedo 
            if cb_albedo.value:
                fig.add_trace(go.Scatter(
                    x=df_sammen["år"], y=df_sammen["Albedo (gjennomsnitt)"],
                    name="Albedo (gjennomsnitt)", mode="lines+markers", yaxis="y3", line=dict(color="green")))
            if cb_reg_albedo.value:
                mask = ~np.isnan(df_sammen["Albedo (gjennomsnitt)"])
                x = df_sammen.loc[mask, "år"]
                y = df_sammen.loc[mask, "Albedo (gjennomsnitt)"]
                if len(x) > 1:
                    z = np.polyfit(x, y, 1)
                    trend = np.polyval(z, x)
                    fig.add_trace(go.Scatter(
                        x=x, y=trend,
                        mode="lines",
                        name="Regresjon albedo",
                        line=dict(width=2, dash="dot", color="darkgreen"),
                        yaxis="y3"
                    ))

            # y-aksene
            axes = dict(
                yaxis=dict(title="Temperatur (gjennomsnitt)", color="red"),
                yaxis2=dict(title="Havnivå (gjennomsnitt)", color="blue", overlaying="y", side="right"),
                yaxis3=dict(title="Albedo (gjennomsnitt)", color="green", anchor="free", overlaying="y", side="left", position=0.06)
            )
            fig.update_layout(
                title="Årlig gjennomsnittlig temperatur, havnivå og albedo-effekt (1992–2025)",
                xaxis=dict(title="År"),
                **axes,
                legend=dict(x=0.01, y=0.99),
                template="plotly_white"
            )
            fig.show()

    # Koble widgets til oppdateringsfunksjonen
    for cb in [cb_temp, cb_havniva, cb_albedo, cb_reg_temp, cb_reg_havniva, cb_reg_albedo]:
        cb.observe(plot_oppdater, names='value')

    display(widgets.HBox([cb_temp, cb_havniva, cb_albedo, cb_reg_temp, cb_reg_havniva, cb_reg_albedo]))
    plot_oppdater()
    display(output)
