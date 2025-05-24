import unittest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Importer modulen (tilpass sti og navn hvis nødvendig)
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "temperaturdata"
sys.path.append(str(src_path))

import dataanalyse  # Importer filnavnet ditt her

class TestDataanalyse(unittest.TestCase):

    def setUp(self):
        # Lag en liten testfil
        self.testfile = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "temperaturdata", "test_temp.csv"))
        df = pd.DataFrame({
            "date": pd.date_range(start="2000-01-01", periods=6, freq="Y"),
            "temperature_2m": [10, 12, 16, 22, -5, 40]
        })
        df.to_csv(self.testfile, index=False)
        # Pek DATAFIL mot denne fila
        self.original_datafil = dataanalyse.DATAFIL
        dataanalyse.DATAFIL = self.testfile

    def tearDown(self):
        # Rydd opp og tilbakestill DATAFIL
        if os.path.isfile(self.testfile):
            os.remove(self.testfile)
        dataanalyse.DATAFIL = self.original_datafil

    def test_les_data_returnerer_dataframe(self):
        df = dataanalyse._les_data()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("year", df.columns)

    def test_statistikk_per_aar(self):
        stats = dataanalyse.statistikk_per_aar()
        self.assertIsInstance(stats, pd.DataFrame)
        self.assertIn("gjennomsnitt", stats.columns)
        self.assertIn("median", stats.columns)
        self.assertIn("stdavvik", stats.columns)

    def test_beskriv_data(self):
        desc = dataanalyse.beskriv_data()
        self.assertTrue("mean" in desc.index)
        self.assertTrue("std" in desc.index)

    def test_pearson_korrelasjon(self):
        r, p = dataanalyse.pearson_korrelasjon()
        self.assertIsInstance(r, float)
        self.assertIsInstance(p, float)
        self.assertTrue(-1 <= r <= 1)

if __name__ == "__main__":
    unittest.main()
