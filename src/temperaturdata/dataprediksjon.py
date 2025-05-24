import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

class TemperaturPrediksjon:
    """
    Klasse for prediktiv analyse med lineær regresjon og visualisering av temperaturdata.
    Feildatasettet får fjernet noen år (settes til NaN), og interpolering skjer på årsgjennomsnitt.
    """

    def __init__(self, sti_rent, sti_feil, kolonne="temperature_2m", tidkol="date", seed=42):
        self.sti_rent = sti_rent
        self.sti_feil = sti_feil
        self.kolonne = kolonne
        self.tidkol = tidkol
        self.seed = seed

        # Leser inn data
        self.df_rent = pd.read_csv(sti_rent)
        self.df_feil = pd.read_csv(sti_feil)
        self.df_feil_mod = self._lag_modifisert_feildata(self.df_feil.copy())
        self.df_interp = self._lag_interpolert_feildata(self.df_feil_mod.copy())

    def _lag_modifisert_feildata(self, df):
        """
        Fjerner noen år (setter NaN på all temp for tilfeldig valgte år).
        """
        np.random.seed(self.seed)
        årstall = pd.to_datetime(df[self.tidkol], errors='coerce').dt.year.dropna().unique()
        n_år = len(årstall)
        n_år_fjern = max(1, int(0.05 * n_år))  # Fjern ~5% av årene helt

        # Velg noen år å fjerne
        år_fjernes = np.random.choice(årstall, size=n_år_fjern, replace=False)
        år_rad = pd.to_datetime(df[self.tidkol], errors='coerce').dt.year.isin(år_fjernes)
        df.loc[år_rad, self.kolonne] = np.nan
        return df

    def _lag_interpolert_feildata(self, df):
        """
        Erstatter urealistiske verdier med NaN og interpolerer ÅRSGJENNOMSNITT,
        så fylles hullene med det interpolerte årsgjennomsnittet.
        """
        # Sorter på dato (bare for sikkerhets skyld)
        df = df.sort_values(self.tidkol)
        # Sett urealistiske til NaN
        df[self.kolonne] = df[self.kolonne].apply(lambda x: x if -40 <= x <= 40 else np.nan)
        # Legg til årskolonne
        df["År"] = pd.to_datetime(df[self.tidkol], errors='coerce').dt.year
        # Finn årsgjennomsnitt (med NaN for hull)
        year_means = df.groupby("År")[self.kolonne].mean()
        # Interpolér årsgjennomsnitt
        year_means_interp = year_means.interpolate()
        # Fyll hullene med det interpolerte årsgjennomsnittet
        def fyll_rad(row):
            if pd.isna(row[self.kolonne]):
                return year_means_interp.loc[row["År"]]
            else:
                return row[self.kolonne]
        df[self.kolonne] = df.apply(fyll_rad, axis=1)
        df = df.drop(columns=["År"])
        return df

    def _beregn_prediksjon(self, df, antall_fremtid=20):
        df = df.dropna(subset=[self.kolonne]).copy()
        år_series = pd.to_datetime(df[self.tidkol], errors='coerce').dt.year
        df = df.assign(År=år_series)
        df = df.dropna(subset=["År"])
        df["År"] = df["År"].astype(int)
        if df.empty:
            raise ValueError("Ingen gyldige datoer igjen i datasettet etter konvertering.")
        stats = df.groupby("År")[self.kolonne].mean().reset_index()
        X = stats[["År"]]
        y = stats[self.kolonne]
        model = LinearRegression()
        model.fit(X, y)
        framtid_år = np.arange(stats["År"].max() + 1, stats["År"].max() + 1 + antall_fremtid)
        framtid = pd.DataFrame({"År": framtid_år})
        framtid["Predikert"] = model.predict(framtid[["År"]])
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        return stats, framtid, model, r2, rmse

    def plot_alle(self):
        """
        Plotter tre forskjellige visualiseringer for alle tre datasett:
        - Linjediagram (trend og prediksjon)
        - Søylediagram
        - Scatterplot (med linær trend)
        Samt en ekstra graf som viser effekten av manglende verdier.
        """
        data = [
            ("Rent datasett", self.df_rent),
            ("Feildatasett (m/år fjernet)", self.df_feil_mod),
            ("Interpolert feildata", self.df_interp)
        ]
        plottitler = {
            "linje": "Linjediagram (trend og prediksjon)",
            "soyle": "Søylediagram (verdier per år og prediksjon)",
            "spredning": "Scatterplot (punkt og trend)"
        }
        for navn, df in data:
            try:
                stats, framtid, model, r2, rmse = self._beregn_prediksjon(df, antall_fremtid=20)
            except ValueError as e:
                print(f"Feil i '{navn}': {e}")
                continue
            # 1. Linjediagram
            plt.figure(figsize=(10, 6))
            plt.style.use("seaborn-v0_8-whitegrid")
            sns.lineplot(x=stats["År"], y=stats[self.kolonne], marker="o", label="Historisk", color="tab:blue")
            sns.lineplot(x=framtid["År"], y=framtid["Predikert"], marker="s", linestyle="--", color="tab:orange", label="Prediksjon")
            plt.plot(stats["År"], model.predict(stats[["År"]]), '--', color="tab:gray", label="Trendlinje")
            plt.title(f"{plottitler['linje']} – {navn}")
            plt.xlabel("År")
            plt.ylabel("Gjennomsnittlig temperatur")
            plt.legend()
            plt.tight_layout()
            plt.show()
            print(f"{navn} (Linjediagram) — R²: {r2:.3f}   RMSE: {rmse:.2f}\n")

            # 2. Søylediagram
            plt.figure(figsize=(10, 6))
            plt.style.use("seaborn-v0_8-whitegrid")
            plt.bar(stats["År"], stats[self.kolonne], color="tab:blue", label="Historisk", alpha=0.7)
            plt.bar(framtid["År"], framtid["Predikert"], color="tab:orange", alpha=0.4, label="Prediksjon")
            plt.plot(stats["År"], model.predict(stats[["År"]]), '--', color="tab:gray", label="Trendlinje")
            plt.title(f"{plottitler['soyle']} – {navn}")
            plt.xlabel("År")
            plt.ylabel("Gjennomsnittlig temperatur")
            plt.legend()
            plt.tight_layout()
            plt.show()
            print(f"{navn} (Søylediagram) — R²: {r2:.3f}   RMSE: {rmse:.2f}\n")

            # 3. Scatterplot
            plt.figure(figsize=(10, 6))
            plt.style.use("seaborn-v0_8-whitegrid")
            plt.scatter(stats["År"], stats[self.kolonne], s=60, color="tab:blue", label="Historisk")
            plt.scatter(framtid["År"], framtid["Predikert"], s=60, marker="s", color="tab:orange", label="Prediksjon")
            plt.plot(stats["År"], model.predict(stats[["År"]]), '--', color="tab:gray", label="Trendlinje")
            plt.title(f"{plottitler['spredning']} – {navn}")
            plt.xlabel("År")
            plt.ylabel("Gjennomsnittlig temperatur")
            plt.legend()
            plt.tight_layout()
            plt.show()
            print(f"{navn} (Scatterplot) — R²: {r2:.3f}   RMSE: {rmse:.2f}\n")

        # Ekstra: graf som viser effekt av manglende verdier
        df_nan = self.df_feil_mod.copy()
        df_nan[self.kolonne] = df_nan[self.kolonne].apply(lambda x: x if -40 <= x <= 40 else np.nan)
        år = pd.to_datetime(df_nan[self.tidkol], errors='coerce').dt.year
        plt.figure(figsize=(10, 4))
        plt.plot(år, df_nan[self.kolonne], '.', label="Målt verdi", color="tab:gray", alpha=0.6)
        nan_mask = df_nan[self.kolonne].isna()
        plt.scatter(år[nan_mask], [np.nan]*nan_mask.sum(), color="red", label="Manglende/feil verdi", zorder=10)
        plt.title("Manglende og feilverdier i feildatasett (røde prikker viser hull)")
        plt.xlabel("År")
        plt.ylabel("Temperatur")
        plt.legend()
        plt.tight_layout()
        plt.show()
