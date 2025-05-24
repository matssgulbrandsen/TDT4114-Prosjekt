import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import plotly.express as px
import plotly.io as pio


pio.renderers.default = "vscode"


class HavnivaaPrediksjon:
    """
    Klasse for prediksjon av havnivå basert på tidligere innsamlede målinger.
    """

    def __init__(self, slutt_år: int = 2100):
        """
        Initialiserer modellen og setter slutten for prediksjon.
        slutt_år : Året det skal predikeres til.
        """
        self.slutt_år = slutt_år
        self.df = None
        self.model = LinearRegression()
        self.mse = None
        self.r2 = None
        self.framtid = None

    def hent_data(self):
        """
        Leser inn havnivådata fra lokal JSON Lines-fil (havnivaadata.json).
        Konverterer relevante kolonner og beregner millimeterverdier.
        """
        datafil = Path(__file__).resolve().parents[2] / "data" / "Havnivådata" / "havnivaadata.json"
        self.df = pd.read_json(datafil, lines=True)

        self.df["iso_time"] = pd.to_datetime(self.df["iso_time"])
        self.df["år"] = self.df["iso_time"].dt.year
        self.df["måned"] = self.df["iso_time"].dt.to_period("M")

        self.df["mean_mm"] = self.df["mean"] * 1000
        self.df["min_mm"] = self.df["min"] * 1000
        self.df["max_mm"] = self.df["max"] * 1000

        self.df["år_decimal"] = self.df["iso_time"].dt.year + self.df["iso_time"].dt.month / 12

    def tren_modell(self):
        """
        Trener lineær regresjonsmodell på treningsdata og evaluerer ytelsen på testdata.

        Vi deler datasettet i to: treningsdata (80 %) og testdata (20 %). Dette gjøres for å kunne evaluere
        modellens evne til predikere data, ikke bare hvor godt den passer til det den er trent på.
        """
        X = self.df[["år_decimal"]]
        y = self.df["mean_mm"].values

        # Del datasettet i trenings- og testsett
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Tren modellen på treningssettet
        self.model.fit(X_train, y_train)

        # Evaluer ytelse på testsettet
        y_pred = self.model.predict(X_test)
        self.mse = mean_squared_error(y_test, y_pred)
        self.r2 = r2_score(y_test, y_pred)

        # Lag fremtidsdata med prediksjoner
        framtid = pd.DataFrame({
            "år_decimal": np.arange(2025, self.slutt_år + 1, 1 / 12)
        })
        framtid["mean_mm_pred"] = self.model.predict(framtid[["år_decimal"]])
        self.framtid = framtid


    def vis_prediksjon(self):
        """
        Visualiserer observerte og predikerte verdier med interaktiv linjegraf.
        """
        fig = px.line(
            self.df,
            x="år_decimal",
            y="mean_mm",
            title="Lineær regresjon: Gjennomsnittlig havnivåstigning over tid",
            labels={"år_decimal": "År", "mean_mm": "Havnivå (mm)"},
            line_shape="linear"
        )

        fig.add_scatter(
            x=self.framtid["år_decimal"],
            y=self.framtid["mean_mm_pred"],
            mode="lines",
            name=f"Predikert til {self.slutt_år}",
            line=dict(color="red")
        )

        fig.update_layout(
            xaxis_title="År",
            yaxis_title="Havnivå (mm)",
            showlegend=True
        )

        fig.show()

    def kjør_prediksjon(self):
        """
        Kjører hele arbeidsflyten: innlasting, modellering og visualisering.
        """
        self.hent_data()
        self.tren_modell()
        self.vis_prediksjon()
        print(f"✅ Modellen er trent. MSE: {self.mse:.2f}, R²: {self.r2:.3f}")


