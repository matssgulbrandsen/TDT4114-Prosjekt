import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio
import ipywidgets as widgets
from IPython.display import display, clear_output
from pathlib import Path

pio.renderers.default = "vscode"

class Havnivaavisualisering:
    """
    Denne klassen brukes for å analysere og visualisere havnivådata fra 1992 til 2025. 

    Den laster inn data fra en JSON-fil, forbereder dataene, og gir flere metoder for å vise ulike typer grafiske visualiseringer. 

    Tilgjengelige visualiseringer inkluderer:
    - Linjediagram for å vise gjennomsnittlig havnivåstigning 
    - Punktdiagram for å vise gjennomsnittlig havnivåstigning 
    - Regresjonslinje for minimums- og maksimumsverdier
    - Glidende gjennomsnitt (12 mnd) for å vise langsiktige trender
    - Boksplott for å vise variasjoner i havnivået per år
    - Interaktive grafer for å vise årlige gjennomsnittlig havnivåstigning

    Metodene bruker forskjellige visualiseringsteknikker, inkludert Matplotlib, Seaborn og Plotly, og støtter også interaktive visualiseringer med widgets for brukervalg.

    Attributter:
        df (DataFrame): Dataene som er lastet fra JSON-filen og forbereder for visualisering.

    Metoder:
        vis_linjediagram()          - Viser et linjediagram av gjennomsnittlig havnivåstigning
        vis_punktdiagram()          - Viser et punktdiagram av gjennomsnittlig havnivåstigning
        vis_min_punktdiagram()      - Viser et punktdiagram med minimumsverdier og regresjonslinje.
        vis_max_punktdiagram()      - Viser et punktdiagram med maksimumsverdier og regresjonslinje.
        vis_glidende_gjennomsnitt() - Viser et glidende gjennomsnitt av havnivåstigning (12 mnd).
        vis_boksplott()             - Viser et boksplott for gjennomsnittlig havnivåstigning per år.
        vis_interaktiv()            - Viser en interaktiv graf for årlig gjennomsnittlig havnivåstigning.
        vis_meny()                  - Gir en interaktivt meny for valg av visualisering.
    """
    def __init__(self, filnavn="havnivaadata.json"):
        datafil = Path(__file__).resolve().parents[2] / "data" / "Havnivådata" / filnavn
        self.df = pd.read_json(datafil, lines=True)
        self._forbered_data()

    def _forbered_data(self):
        self.df["iso_time"] = pd.to_datetime(self.df["iso_time"])
        self.df["år"] = self.df["iso_time"].dt.year
        self.df["måned"] = self.df["iso_time"].dt.tz_localize(None).dt.to_period("M")
        self.df["mean_mm"] = self.df["mean"] * 1000
        self.df["min_mm"] = self.df["min"] * 1000
        self.df["max_mm"] = self.df["max"] * 1000

    def vis_linjediagram(self):
        plt.figure(figsize=(12, 5))
        sns.lineplot(data=self.df, x="iso_time", y="mean_mm", color="blue")
        plt.title("Gjennomsnittlig havnivåstigning fra 1992 til 2025 (mm)")
        plt.xlabel("Tid")
        plt.ylabel("Havnivåstigning i millimeter")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def vis_punktdiagram(self):
        df_mnd = self.df[["måned", "mean_mm"]].dropna()
        df_mnd["dato"] = df_mnd["måned"].dt.to_timestamp()
        plt.figure(figsize=(12, 5))
        plt.scatter(df_mnd["dato"], df_mnd["mean_mm"], color="green", alpha=0.7, s=10)
        plt.title("Gjennomsnittlig havnivåstigning fra 1992 til 2025 (mm)")
        plt.xlabel("Tid")
        plt.ylabel("Havnivåstigning i millimeter")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def vis_regresjon(self):
        df_mnd = self.df[["måned", "mean_mm", "min_mm", "max_mm"]].dropna()
        df_mnd["tid"] = df_mnd["måned"].dt.to_timestamp()
        df_mnd["årstall"] = df_mnd["tid"].dt.year + df_mnd["tid"].dt.month / 12

        plt.figure(figsize=(14, 6))
        sns.regplot(x="årstall", y="mean_mm", data=df_mnd, label="Gjennomsnitt", color="blue", scatter_kws={'s': 10})
        sns.regplot(x="årstall", y="min_mm", data=df_mnd, label="Minimum", color="green", scatter_kws={'s': 10})
        sns.regplot(x="årstall", y="max_mm", data=df_mnd, label="Maksimum", color="red", scatter_kws={'s': 10})
        plt.title("Regresjonsanalyse av havnivå (minimum, maksimum og gjennomsnitt)")
        plt.xlabel("År")
        plt.ylabel("Havnivå i millimeter")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()        

    def vis_min_punktdiagram(self, vis_regresjon=True):
        df_mnd = self.df[["måned", "min_mm"]].dropna()
        df_mnd["dato"] = df_mnd["måned"].dt.to_timestamp()
        df_mnd["årstall"] = df_mnd["dato"].dt.year + df_mnd["dato"].dt.month / 12

        plt.figure(figsize=(14, 5))
        sns.scatterplot(x="årstall", y="min_mm", data=df_mnd, color="green", label="Minimumsverdier", s=12)

        if vis_regresjon:
            sns.regplot(x="årstall", y="min_mm", data=df_mnd, scatter=False, color="black", line_kws={'label': 'Regresjonslinje'})

        plt.xlim(df_mnd["årstall"].min() - 1, df_mnd["årstall"].max() + 1)
        plt.title("Minimum havnivåmåling for hver måned")
        plt.xlabel("År")
        plt.ylabel("Havnivå (mm)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def vis_max_punktdiagram(self, vis_regresjon=True):
        df_mnd = self.df[["måned", "max_mm"]].dropna()
        df_mnd["dato"] = df_mnd["måned"].dt.to_timestamp()
        df_mnd["årstall"] = df_mnd["dato"].dt.year + df_mnd["dato"].dt.month / 12

        plt.figure(figsize=(14, 5))
        sns.scatterplot(x="årstall", y="max_mm", data=df_mnd, color="red", label="Maksimumsverdier", s=12)

        if vis_regresjon:
            sns.regplot(x="årstall", y="max_mm", data=df_mnd, scatter=False, color="black", line_kws={'label': 'Regresjonslinje'})

        plt.xlim(df_mnd["årstall"].min() - 1, df_mnd["årstall"].max() + 1)
        plt.title("Maksimum havnivå for hver måned")
        plt.xlabel("År")
        plt.ylabel("Havnivå (mm)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def vis_glidende_gjennomsnitt(self):
        df_copy = self.df.copy()
        df_copy["glidende_mean"] = df_copy["mean_mm"].rolling(window=12, min_periods=1).mean()
        plt.figure(figsize=(12, 5))
        plt.plot(df_copy["iso_time"], df_copy["mean_mm"], label="Rådata", alpha=0.3)
        plt.plot(df_copy["iso_time"], df_copy["glidende_mean"], label="12 måneders glidende gjennomsnitt", color="red")
        plt.title("Moving average av gjennomsnittlig havnivåstigning (12 måneder)")
        plt.xlabel("Tid")
        plt.ylabel("Havnivåstigning i millimeter")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def vis_boksplott(self):
        plt.figure(figsize=(15, 6))
        self.df.boxplot(column="mean_mm", by="år", grid=True, showfliers=False)
        plt.title("Gjennomsnittlig havnivåstigning per år (1992–2025)")
        plt.suptitle("")
        plt.xlabel("År")
        plt.xticks(rotation=45)
        plt.ylabel("Havnivåstigning i millimeter")
        plt.tight_layout()
        plt.show()

    def vis_interaktiv(self):
        df_årlig = self.df.groupby("år")["mean_mm"].mean().reset_index()
        fig = px.line(
            df_årlig,
            x="år",
            y="mean_mm",
            title="Årlig gjennomsnittlig havnivåstigning (1992–2025)",
            labels={"mean_mm": "Havnivåstigning i millimeter", "år": "År"}
        )
        fig.update_layout(hovermode="x unified")
        fig.show()

    def vis_meny(self):
        output_tekst = widgets.Output()

        valg_boks = widgets.Dropdown(
            options=[
                ("📈 Linjediagram: Gjennomsnittlig havnivåstigning", "linje"),
                ("🔹 Punktdiagram: Gjennomsnittlig havnivåstigning", "punkt"),
                ("📉 Regresjon: Min, maks, gjennomsnitt", "regresjon"),
                ("📏 Moving average (12 mnd)", "glidende"),
                ("📦 Boksplott: Gjennomsnittlig havnivåstigning per år", "boks"),
                ("🌍 Interaktiv graf: Årlig gjennomsnittlig havnivåstigning", "interaktiv"),
                ("🔻 Minimum: Punktdiagram med trend", "minpunkt"),
                ("🔺 Maksimum: Punktdiagram med trend", "maxpunkt")
            ],
            description="Velg graf:",
            style={"description_width": "initial"},
            layout=widgets.Layout(width="70%")
        )

        regresjons_toggle = widgets.Checkbox(
            value=True,
            description="Vis regresjonslinje (gjelder kun minimum/maks)",
            indent=False
        )

        knapp = widgets.Button(description="Vis graf")

        def vis_valg(b):
            output_tekst.clear_output()
            with output_tekst:
                valg = valg_boks.value
                vis_reg = regresjons_toggle.value

                if valg == "linje":
                    self.vis_linjediagram()
                elif valg == "punkt":
                    self.vis_punktdiagram()
                elif valg == "regresjon":
                    self.vis_regresjon()
                elif valg == "glidende":
                    self.vis_glidende_gjennomsnitt()
                elif valg == "boks":
                    self.vis_boksplott()
                elif valg == "interaktiv":
                    self.vis_interaktiv()
                elif valg == "minpunkt":
                    self.vis_min_punktdiagram(vis_regresjon=vis_reg)
                elif valg == "maxpunkt":
                    self.vis_max_punktdiagram(vis_regresjon=vis_reg)

        knapp.on_click(vis_valg)
        return widgets.VBox([valg_boks, regresjons_toggle, knapp, output_tekst])
