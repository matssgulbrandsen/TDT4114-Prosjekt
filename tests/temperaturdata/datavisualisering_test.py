import unittest
import sys
import pandas as pd
from pathlib import Path

# Legg til src/temperaturdata i importstien
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "temperaturdata"
sys.path.append(str(src_path))

from datavisualisering import Temperaturmeny

class TestTemperaturmeny(unittest.TestCase):

    def setUp(self):
        # Lager en testfil i riktig mappe
        self.testfil = Path(__file__).resolve().parents[2] / "data" / "temperaturdata" / "test_temp.csv"
        df = pd.DataFrame({
            "date": pd.date_range(start="2010-01-01", periods=10, freq="Y"),
            "temperature_2m": [5, 6, 10, 15, 8, 7, 12, 14, 9, 11]
        })
        self.testfil.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.testfil, index=False)

    def tearDown(self):
        # Sletter testfila etterpå
        if self.testfil.exists():
            self.testfil.unlink()

    def test_init(self):
        # Test at klassen kan opprettes og har forventede attributter
        meny = Temperaturmeny(filnavn="test_temp.csv")
        self.assertIsInstance(meny.df, pd.DataFrame)
        self.assertIsInstance(meny.stats, pd.DataFrame)
        self.assertIn("gjennomsnitt", meny.stats.columns)

    def test_plot_interaktiv_kan_kalles(self):
        # Test at plot_interaktiv kan kjøres uten å feile
        meny = Temperaturmeny(filnavn="test_temp.csv")
        try:
            meny.plot_interaktiv()
            resultat = True
        except Exception as e:
            print(e)
            resultat = False
        self.assertTrue(resultat)

if __name__ == "__main__":
    unittest.main()
