import unittest
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import builtins

# Legg til src/Havnådata i path
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "Havnivådata"
sys.path.append(str(src_path))

from Databehandling import (
    rens_manglende_verdier,
    demonstrer_rensing_av_manglende_verdier,
    sett_usannsynlige_til_nan
)

class TestDatabehandling(unittest.TestCase):
    def setUp(self):
        # Arrange: Forbered test-DataFrame og undertrykk print
        self.df = pd.DataFrame({
            "A": [1, 2, np.nan, 4, 5],
            "B": [10, np.nan, 30, 40, 50]
        })
        self.original_print = builtins.print
        builtins.print = lambda *args, **kwargs: None

    def tearDown(self):
        # Tilbakestill print etter test
        builtins.print = self.original_print

    def test_rens_mean(self):
        # Act
        df_renset = rens_manglende_verdier(self.df.copy(), metode="mean")
        # Assert
        self.assertFalse(df_renset.isnull().values.any())

    def test_rens_median(self):
        df_renset = rens_manglende_verdier(self.df.copy(), metode="median")
        self.assertFalse(df_renset.isnull().values.any())

    def test_rens_interpolate(self):
        df_renset = rens_manglende_verdier(self.df.copy(), metode="interpolate")
        self.assertFalse(df_renset.isnull().values.any())

    def test_rens_drop(self):
        # Act
        df_renset = rens_manglende_verdier(self.df.copy(), metode="drop")
        # Assert
        self.assertFalse(df_renset.isnull().values.any())
        self.assertLess(len(df_renset), len(self.df))  # Drop skal fjerne rader

    def test_rens_invalid_metode_feiler(self):
        # Assert: Verifiser at ugyldig metode gir ValueError (negativ test)
        with self.assertRaises(ValueError):
            rens_manglende_verdier(self.df.copy(), metode="ugyldig")

    def test_sett_usannsynlige_verdier_til_nan(self):
        # Arrange
        df = pd.DataFrame({"mean": [0.0, 0.3, 0.7, -0.4, -0.9]})
        grenser = {"mean": [-0.5, 0.5]}
        # Act
        df_renset = sett_usannsynlige_til_nan(df, grenser)
        # Assert
        self.assertTrue(df_renset["mean"].isnull().sum() > 0)

    def test_demonstrer_rensing_returnerer_dataframe(self):
        # Arrange
        df = pd.DataFrame({"x": np.arange(100), "y": np.random.randn(100)})
        # Act
        df_renset = demonstrer_rensing_av_manglende_verdier(df, metode="ffill")
        # Assert
        self.assertIsInstance(df_renset, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()
