import unittest
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Legg til src/temperaturdata i importstien
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "temperaturdata"
sys.path.append(str(src_path))
from dataprediksjon import TemperaturPrediksjon

class TestTemperaturPrediksjon(unittest.TestCase):

    def setUp(self):
        # Lager testdata og skriver til midlertidige csv-filer
        antall = 100
        år = np.random.randint(1990, 2020, size=antall)
        temp = np.random.normal(7, 5, size=antall)
        temp[10] = 60   # For høy temperatur
        temp[20] = -50  # For lav temperatur
        temp[30] = np.nan  # Manglende verdi
        dato = pd.to_datetime([f"{årstall}-06-01" for årstall in år])
        df = pd.DataFrame({"date": dato, "temperature_2m": temp})

        self.tmpdir = Path("./__test_tempdir")
        self.tmpdir.mkdir(exist_ok=True)
        self.sti_rent = str(self.tmpdir / "rent.csv")
        self.sti_feil = str(self.tmpdir / "feil.csv")
        df.to_csv(self.sti_rent, index=False)
        df.to_csv(self.sti_feil, index=False)

    def tearDown(self):
        # Sletter testfiler og mappe etter testen er ferdig
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_init_og_datasett(self):
        # Sjekker at objekter og datasett blir laget riktig
        tp = TemperaturPrediksjon(self.sti_rent, self.sti_feil)
        self.assertIsInstance(tp.df_rent, pd.DataFrame)
        self.assertIsInstance(tp.df_feil_mod, pd.DataFrame)
        self.assertIsInstance(tp.df_interp, pd.DataFrame)
        # Sjekker at interpolert datasett ikke har manglende verdier
        self.assertEqual(tp.df_interp["temperature_2m"].isna().sum(), 0)

    def test_beregn_prediksjon(self):
        # Sjekker at modelltrening og prediksjon fungerer
        tp = TemperaturPrediksjon(self.sti_rent, self.sti_feil)
        stats, framtid, model, r2, rmse = tp._beregn_prediksjon(tp.df_rent, antall_fremtid=5)
        self.assertIsInstance(stats, pd.DataFrame)
        self.assertIsInstance(framtid, pd.DataFrame)
        self.assertTrue(hasattr(model, "predict"))
        self.assertIsInstance(r2, float)
        self.assertIsInstance(rmse, float)

    def test_plot_alle(self):
        # Sjekker at plot_alle kan kjøres uten feil (plot vises ikke)
        tp = TemperaturPrediksjon(self.sti_rent, self.sti_feil)
        import matplotlib.pyplot as plt
        import seaborn as sns
        plt.show = lambda *a, **k: None
        sns.lineplot = lambda *a, **k: None
        plt.bar = lambda *a, **k: None
        plt.scatter = lambda *a, **k: None
        plt.plot = lambda *a, **k: None
        try:
            tp.plot_alle()
        except Exception as e:
            self.fail(f"plot_alle() feilet: {e}")

if __name__ == "__main__":
    unittest.main()
