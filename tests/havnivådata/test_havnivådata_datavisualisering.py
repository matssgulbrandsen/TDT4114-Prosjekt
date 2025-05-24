import unittest
import sys
import matplotlib.pyplot as plt
from pathlib import Path

# Legg til src/Havnådata i sys.path
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "Havnivådata"
sys.path.append(str(src_path))

from Datavisualisering import Havnivaavisualisering

class TestHavnivaavisualisering(unittest.TestCase):
    def setUp(self):
        # Arrange: Opprett objektet som skal testes
        self.visual = Havnivaavisualisering()

    def test_data_lasting_returnerer_gyldig_dataframe(self):
        # Act: Tilgang til DataFrame
        df = self.visual.df

        # Assert: Dataen skal være lastet og inneholde riktige kolonner
        self.assertFalse(df.empty, "DataFrame skal ikke være tom")
        for kol in ["iso_time", "år", "måned", "mean_mm", "min_mm", "max_mm"]:
            self.assertIn(kol, df.columns)

    def test_vis_linjediagram_kjører_uten_plot(self):
        # Act og Assert
        try:
            self.visual.vis_linjediagram(show=False)
        except Exception as e:
            self.fail(f"vis_linjediagram() feilet: {e}")

    def test_vis_punktdiagram_kjører_uten_plot(self):
        # Act og Assert
        try:
            self.visual.vis_punktdiagram(show=False)
        except Exception as e:
            self.fail(f"vis_punktdiagram() feilet: {e}")

    def test_vis_min_punktdiagram_kjører_med_og_uten_regresjon(self):
        # Act og Assert for begge mulighetene
        try:
            self.visual.vis_min_punktdiagram(vis_regresjon=False, show=False)
            self.visual.vis_min_punktdiagram(vis_regresjon=True, show=False)
        except Exception as e:
            self.fail(f"vis_min_punktdiagram() feilet: {e}")

    def test_vis_max_punktdiagram_kjører_med_og_uten_regresjon(self):
        # Act og Assert for begge mulighetene
        try:
            self.visual.vis_max_punktdiagram(vis_regresjon=False, show=False)
            self.visual.vis_max_punktdiagram(vis_regresjon=True, show=False)
        except Exception as e:
            self.fail(f"vis_max_punktdiagram() feilet: {e}")

    def test_vis_glidende_gjennomsnitt_kjører_uten_plot(self):
        # Act og Assert
        try:
            self.visual.vis_glidende_gjennomsnitt(show=False)
        except Exception as e:
            self.fail(f"vis_glidende_gjennomsnitt() feilet: {e}")

    def test_vis_boksplott_kjører_uten_plot(self):
        # Act og Assert
        try:
            self.visual.vis_boksplott(show=False)
        except Exception as e:
            self.fail(f"vis_boksplott() feilet: {e}")

    def test_vis_interaktiv_plotly_kjører(self):
        # Act og Assert: Plotly sin show() kan ikke slås av, men skal ikke feile
        try:
            self.visual.vis_interaktiv()
        except Exception as e:
            self.fail(f"vis_interaktiv() feilet: {e}")

    def test_vis_meny_returnerer_widget(self):
        # Act
        meny = self.visual.vis_meny()

        # Assert
        self.assertIsNotNone(meny, "vis_meny() skal returnere et VBox-widgetobjekt")

if __name__ == '__main__':
    unittest.main()
