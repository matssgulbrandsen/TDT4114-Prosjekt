import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import ipywidgets as widgets
from albedo_effekt.datavisualisering import Visualisering

class PrediksjonVisualisering:
    def __init__(self):
        self.visualisering = Visualisering()

    def beregn_prediksjonsmodell(self, stats=None, antall_fremtid=5):
        """
        Lager stats-df og regresjonsmodell for prediksjon.
        Kan bruke stats fra hent_stats_dataframe eller levere inn egen.
        Returnerer stats (historisk), framtid (predikert), og modell.
        """
        if stats is None:
            stats = self.visualisering.hent_stats_dataframe()
        stats = stats.dropna()

        X = stats[["År"]]
        y = stats["Gjennomsnittlig albedo"]
        model = LinearRegression()
        model.fit(X, y)

        framtid = pd.DataFrame({"År": np.arange(stats["År"].max() + 1, stats["År"].max() + 1 + antall_fremtid)})
        framtid["Predikert"] = model.predict(framtid)

        return stats, framtid, model

    def plot_prediksjon(self, stats, framtid, plottype="linje"):
        """
        Visualiserer historiske data + fremtidsprediksjon.
        plottype: 'linje', 'soyle', eller 'spredning'
        """
        if plottype == "linje":
            plt.figure(figsize=(10, 5))
            sns.lineplot(data=stats, x="År", y="Gjennomsnittlig albedo", marker="o", label="Historisk")
            sns.lineplot(data=framtid, x="År", y="Predikert", marker="o", linestyle="--", color="orange", label="Predikert")
            sns.regplot(data=stats, x="År", y="Gjennomsnittlig albedo", scatter=False, color="gray", ci=None, label="Trend")
            plt.title("Linjediagram: Gjennomsnittlig albedo med trendlinje og prediksjon")
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.legend()
            plt.tight_layout()
            plt.show()

        elif plottype == "soyle":
            plt.figure(figsize=(10, 5))
            plt.bar(stats["År"], stats["Gjennomsnittlig albedo"], color="skyblue", label="Historisk")
            plt.bar(framtid["År"], framtid["Predikert"], color="orange", alpha=0.6, label="Predikert")
            sns.regplot(data=stats, x="År", y="Gjennomsnittlig albedo", scatter=False, color="black", ci=None, label="Trend", line_kws={"linestyle": "--"})
            plt.title("Søylediagram: Gjennomsnittlig albedo med trend og prediksjon")
            plt.xlabel("År")
            plt.ylabel("Albedo")
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.legend()
            plt.tight_layout()
            plt.show()

        elif plottype == "spredning":
            plt.figure(figsize=(10, 5))
            sns.scatterplot(data=stats, x="År", y="Gjennomsnittlig albedo", s=80, label="Historisk")
            sns.scatterplot(data=framtid, x="År", y="Predikert", s=80, color="orange", label="Predikert")
            sns.regplot(data=stats, x="År", y="Gjennomsnittlig albedo", scatter=False, color="gray", ci=None, label="Trend")
            plt.title("Scatterplot: Historiske punkter og prediksjon med trendlinje")
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.legend()
            plt.tight_layout()
            plt.show()

    def vis_prediksjon_meny(self, stats=None, antall_fremtid=5):
        """
        Interaktiv meny for å vise prediktiv analyse på valgfritt plott.
        stats hentes automatisk hvis ikke gitt.
        """
        if stats is None:
            stats = self.visualisering.hent_stats_dataframe()
        stats, framtid, modell = self.beregn_prediksjonsmodell(stats, antall_fremtid)

        meny = widgets.Dropdown(
            options=[("Linjediagram", "linje"), ("Søylediagram", "soyle"), ("Scatterplot", "spredning")],
            value="linje",
            description="Velg visning:"
        )

        def _vis_plot(plottype):
            self.plot_prediksjon(stats, framtid, plottype=plottype)
        
        widgets.interact(_vis_plot, plottype=meny)

    def plot_manglende_verdier_effekt(self, stats):
        """
        Plotter hvordan manglende verdier (2013 og 2022) og interpolasjon påvirker trendlinje og tolkning.
        """
        X_full = stats[["År"]]
        y_full = stats["Gjennomsnittlig albedo"]
        model_full = LinearRegression()
        model_full.fit(X_full, y_full)
        trend_full = model_full.predict(X_full)

        stats_missing = stats.copy()
        stats_missing.loc[stats_missing["År"].isin([2013, 2022]), "Gjennomsnittlig albedo"] = np.nan
        stats_interp = stats_missing.copy()
        stats_interp["Gjennomsnittlig albedo"] = stats_interp["Gjennomsnittlig albedo"].interpolate(method="linear")

        X_interp = stats_interp[["År"]]
        y_interp = stats_interp["Gjennomsnittlig albedo"]
        model_interp = LinearRegression()
        model_interp.fit(X_interp, y_interp)
        trend_interp = model_interp.predict(X_interp)

        plt.figure(figsize=(12, 6))
        sns.scatterplot(data=stats, x="År", y="Gjennomsnittlig albedo", s=70, label="Ekte data", color="blue")
        plt.plot(stats["År"], trend_full, '-', color="blue", label="Trendlinje – ekte data")
        sns.scatterplot(data=stats_interp, x="År", y="Gjennomsnittlig albedo", s=70, color="orange", label="Interpolert")
        plt.plot(stats["År"], trend_interp, '--', color="orange", label="Trendlinje – interpolert data")
        for år in [2013, 2022]:
            plt.axvline(x=år, linestyle=":", color="red", alpha=0.7)
            plt.text(år, plt.ylim()[1]*0.95, "Manglet", color="red", ha="center", fontsize=9)
        plt.title("Effekt av manglende verdier og interpolasjon på trendlinje for albedo")
        plt.xlabel("År")
        plt.ylabel("Gjennomsnittlig albedo")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()

        stigning_full = model_full.coef_[0]
        stigning_interp = model_interp.coef_[0]
        diff = stigning_interp - stigning_full
        print(f"Trend (ekte): {stigning_full:.4f} per år, Trend (interpolert): {stigning_interp:.4f} per år.")
        print(f"Forskjell i trendstigning (på grunn av manglende/interpolerte verdier): {diff:.4f}")

    def plot_helperiode_med_prediksjon(self, stats, antall_fremtid=5):
        """
        Viser:
        - Historiske punkter (blå sirkler)
        - Trendlinje for hele perioden (ekte data)
        - Trendlinje og punkter for interpolert data (kun 2013 og 2022)
        - Fremtidsprediksjon som blå linje videre fra ekte trend
        """
        # Modell og trend på ekte data
        X_full = stats[["År"]]
        y_full = stats["Gjennomsnittlig albedo"].values
        model_full = LinearRegression()
        model_full.fit(X_full, y_full)
        trend_full = model_full.predict(X_full)
        # Fremtidsprediksjon fra ekte modell
        framtid = pd.DataFrame({"År": np.arange(stats["År"].max()+1, stats["År"].max()+1+antall_fremtid)})
        framtid["Predikert_full"] = model_full.predict(framtid[["År"]])

        # Lag interpolerte verdier bare for 2013 og 2022
        stats_missing = stats.copy()
        stats_missing.loc[stats_missing["År"].isin([2013, 2022]), "Gjennomsnittlig albedo"] = np.nan
        stats_interp = stats_missing.copy()
        stats_interp["Gjennomsnittlig albedo"] = stats_interp["Gjennomsnittlig albedo"].interpolate(method="linear")
        interpolert_aar = [2013, 2022]
        mask_interp = stats["År"].isin(interpolert_aar)

        # Interpolert trend for sammenligning (på hele rekka)
        X_interp = stats_interp[["År"]]
        y_interp = stats_interp["Gjennomsnittlig albedo"].values
        model_interp = LinearRegression()
        model_interp.fit(X_interp, y_interp)
        trend_interp = model_interp.predict(X_interp)
        framtid["Predikert_interp"] = model_interp.predict(framtid[["År"]])

        # Plotting
        plt.figure(figsize=(12, 6))
        plt.scatter(stats.loc[~mask_interp, "År"], stats.loc[~mask_interp, "Gjennomsnittlig albedo"],
                    color="blue", label="Ekte data", s=70, zorder=2)
        plt.scatter(stats_interp.loc[mask_interp, "År"], stats_interp.loc[mask_interp, "Gjennomsnittlig albedo"],
                    color="orange", label="Interpolert (2013/2022)", s=100, marker="s", zorder=3)
        plt.plot(stats["År"], trend_full, '-', color="blue", label="Trendlinje (ekte)", zorder=1)
        plt.plot(stats_interp["År"], trend_interp, '--', color="orange", label="Trendlinje (interpolert)", zorder=1)
        plt.plot(np.concatenate([stats["År"], framtid["År"]]),
                np.concatenate([trend_full, framtid["Predikert_full"].values]),
                '-', color="blue", alpha=0.5, label="Prediksjon (ekte)", zorder=1)
        plt.plot(np.concatenate([stats["År"], framtid["År"]]),
                np.concatenate([trend_interp, framtid["Predikert_interp"].values]),
                '--', color="orange", alpha=0.5, label="Prediksjon (interpolert)", zorder=1)

        # Tekst markører for manglende år
        for år in interpolert_aar:
            plt.text(år, plt.ylim()[1]*0.97, "Manglet", color="red", ha="center", fontsize=9)

        plt.title("Hele perioden + fremtidsprediksjon\nEffekt av manglende/interpolerte år")
        plt.xlabel("År")
        plt.ylabel("Gjennomsnittlig albedo")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()

        # Beregn og skriv ut forskjell i stigning
        stigning_full = model_full.coef_[0]
        stigning_interp = model_interp.coef_[0]
        diff = stigning_interp - stigning_full
        print(f"Stigning ekte data: {stigning_full:.5f}")
        print(f"Stigning interpolert: {stigning_interp:.5f}")
        print(f"Forskjell i stigning: {diff:.5f}")


