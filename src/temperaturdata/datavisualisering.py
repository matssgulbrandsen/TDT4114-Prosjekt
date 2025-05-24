import pandas as pd
import numpy as np
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display
from pathlib import Path

class Temperaturmeny:
    """
    Klasse for interaktiv visualisering av årlig temperaturstatistikk.
    Brukes i Jupyter Notebook og tilbyr et dynamisk Plotly-linjeplot
    hvor man kan velge å vise/ikke vise følgende:
      - Årlig gjennomsnitt
      - Årlig median
      - Årlig standardavvik
      - Glidende gjennomsnitt (5 år)
      - Lineær trendlinje (OLS) for årlig gjennomsnitt

    Datakilde: temperaturdata.csv fra prosjektets /data/temperaturdata/.

    """

    def __init__(self, filnavn="temperaturdata.csv"):
        """
        Leser inn temperaturdata og forbereder DataFrame med årstall og årlig statistikk.

        """
        # Finn datasettet uansett hvor scriptet kjøres fra
        datafil = Path(__file__).resolve().parents[2] / "data" / "temperaturdata" / filnavn
        self.df = pd.read_csv(datafil)
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["år"] = self.df["date"].dt.year

        # Beregn årlig statistikk
        self.stats = self.df.groupby("år")["temperature_2m"].agg(
            gjennomsnitt="mean",
            median="median",
            stdavvik="std"
        ).reset_index()
        # Glidende gjennomsnitt (over 5 år)
        self.stats["glidende_5"] = self.stats["gjennomsnitt"].rolling(window=5, min_periods=1).mean()

    def plot_interaktiv(self):
        """
        Viser interaktivt Plotly-linjeplot for årlig temperaturstatistikk.
        Bruk knapper/buttons for å velge hvilke mål som skal vises:
            - Årlig gjennomsnitt
            - Årlig median
            - Årlig standardavvik
            - Glidende gjennomsnitt (5 år)
            - Lineær trendlinje (OLS) for årlig gjennomsnitt
        """
        # Widgets for valg
        cb_mean = widgets.Checkbox(value=True, description="Årlig gjennomsnitt")
        cb_median = widgets.Checkbox(value=True, description="Årlig median")
        cb_std = widgets.Checkbox(value=False, description="Årlig standardavvik")
        cb_glidende = widgets.Checkbox(value=False, description="Glidende gjennomsnitt (5 år)")
        cb_trend = widgets.Checkbox(value=False, description="Lineær trend (OLS)")
        output = widgets.Output()

        def plot_oppdater(*args):
            output.clear_output()
            with output:
                fig = go.Figure()
                x = self.stats["år"]

                # Tegn de linjene som er valgt
                if cb_mean.value:
                    fig.add_trace(go.Scatter(
                        x=x, y=self.stats["gjennomsnitt"], mode="lines+markers", name="Gjennomsnitt (år)"
                    ))
                if cb_median.value:
                    fig.add_trace(go.Scatter(
                        x=x, y=self.stats["median"], mode="lines+markers", name="Median (år)"
                    ))
                if cb_std.value:
                    fig.add_trace(go.Scatter(
                        x=x, y=self.stats["stdavvik"], mode="lines+markers", name="Standardavvik (år)"
                    ))
                if cb_glidende.value:
                    fig.add_trace(go.Scatter(
                        x=x, y=self.stats["glidende_5"], mode="lines",
                        name="Glidende snitt (5 år)", line=dict(width=3, dash='dash')
                    ))
                if cb_trend.value:
                    # Trendlinje kun på gjennomsnitt (OLS)
                    mask = ~np.isnan(self.stats["gjennomsnitt"])
                    x_trend = x[mask]
                    y_trend = self.stats["gjennomsnitt"][mask]
                    z = np.polyfit(x_trend, y_trend, 1)
                    trend = np.polyval(z, x_trend)
                    fig.add_trace(go.Scatter(
                        x=x_trend, y=trend,
                        mode="lines",
                        name="Lineær trend (OLS)",
                        line=dict(width=2, dash="dot", color="black")
                    ))
                fig.update_layout(
                    title="Årlig temperaturstatistikk (velg hvilke mål som skal vises)",
                    xaxis_title="År",
                    yaxis_title="Temperatur (°C)",
                    legend_title="Mål",
                    template="plotly_white"
                )
                fig.show()

        # Koble widgets til oppdateringsfunksjon
        for cb in [cb_mean, cb_median, cb_std, cb_glidende, cb_trend]:
            cb.observe(plot_oppdater, names='value')

        plot_oppdater()
        meny = widgets.HBox([cb_mean, cb_median, cb_std, cb_glidende, cb_trend])
        display(meny)
        display(output)
