import unittest
import sys
import pandas as pd
from pathlib import Path
import builtins

# Legg til src/Havnådata i path
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "Havnivådata"
sys.path.append(str(src_path))

from Dataanalyse import (
    beregn_korrelasjon_mnd_vs_mean,
    beregn_statistikk_numpy,
    beskriv_statistikk,
    finn_mistenkelige_hopp
)

class TestDataanalyse(unittest.TestCase):
    def setUp(self):
        # Undertrykk print for ren testrapport
        self.original_print = builtins.print
        builtins.print = lambda *args, **kwargs: None
        self.datafil = str(project_root / "data" / "Havnivådata" / "havnivaadata.json")

    def tearDown(self):
        builtins.print = self.original_print

    def test_beregn_korrelasjon_mnd_vs_mean(self):
        # Act
        beregn_korrelasjon_mnd_vs_mean(self.datafil)  # Returneres ikke, bare evalueres

        # Assert
        self.assertTrue(True)

    def test_beregn_statistikk_numpy_returnerer_dict(self):
        # Act
        resultater = beregn_statistikk_numpy(self.datafil)

        # Assert
        self.assertIsInstance(resultater, dict)
        for key in ["min", "mean", "max"]:
            self.assertIn(key, resultater)
            self.assertIn("gjennomsnitt", resultater[key])
            self.assertIn("median", resultater[key])
            self.assertIn("standardavvik", resultater[key])

    def test_beskriv_statistikk_returnerer_dataframe(self):
        # Act
        df_desc = beskriv_statistikk(self.datafil)

        # Assert
        self.assertIsInstance(df_desc, pd.DataFrame)
        for kol in ["min", "mean", "max"]:
            self.assertIn(kol, df_desc.columns)

    def test_finn_mistenkelige_hopp_returnerer_riktig_format(self):
        # Act
        df_outliers = finn_mistenkelige_hopp(self.datafil, kolonne="mean", grense_faktor=3.0)

        # Assert
        self.assertIsInstance(df_outliers, pd.DataFrame)
        for kol in ["iso_time", "mean", "mean_diff"]:
            self.assertIn(kol, df_outliers.columns)

if __name__ == '__main__':
    unittest.main()
