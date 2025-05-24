import unittest
import sys
import pandas as pd
from pathlib import Path

# Legg til src/Havnivådata i importstien
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "Havnivådata"
sys.path.append(str(src_path))

from Dataprediksjon import HavnivaaPrediksjon

class TestHavnivaaPrediksjon(unittest.TestCase):
    def setUp(self):
        self.model = HavnivaaPrediksjon(slutt_år=2100)

    def test_data_lasting_returnerer_forventede_kolonner(self):
        # Arrange og Act
        self.model.hent_data()

        # Assert
        self.assertFalse(self.model.df.empty, "DataFrame skal ikke være tom")
        for kol in ["iso_time", "år", "måned", "mean_mm", "min_mm", "max_mm", "år_decimal"]:
            self.assertIn(kol, self.model.df.columns)

    def test_modell_trener_og_beregner_riktig(self):
        # Arrange
        self.model.hent_data()

        # Act
        self.model.tren_modell()

        # Assert
        self.assertIsNotNone(self.model.mse, "MSE skal være beregnet")
        self.assertIsNotNone(self.model.r2, "R² skal være beregnet")
        self.assertFalse(self.model.framtid.empty, "Fremtids-DataFrame skal ikke være tom")
        self.assertIn("mean_mm_pred", self.model.framtid.columns)

    def test_kjor_prediksjon_kjører_helt_uten_visualisering(self):
        # Arrange
        self.model.vis_prediksjon = lambda: None  # Mock for å unngå åpning av graf

        # Act og assert
        try:
            self.model.kjør_prediksjon()
        except Exception as e:
            self.fail(f"kjør_prediksjon() feilet: {e}")

    def test_negativ_modell_trening_uten_data_feiler(self):
        # Arrange: hopp over hent_data()

        # Act og Assert
        with self.assertRaises(Exception):
            self.model.tren_modell()

if __name__ == "__main__":
    unittest.main()
