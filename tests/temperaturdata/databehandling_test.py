import unittest
import pandas as pd
import os
import sys
from pathlib import Path

# Legg til src/temperaturdata i importstien (justér sti hvis nødvendig)
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "temperaturdata"
sys.path.append(str(src_path))

import databehandling  # Pass på at dette matcher filnavnet ditt

class TestDatabehandling(unittest.TestCase):

    def setUp(self):
        # Opprett en enkel liten testfil for bruk i testene
        self.testfile = "test_temp.csv"
        df = pd.DataFrame({
            "temperature_2m": [10, 15, None, -100, 30, 100]
        })
        datadir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "temperaturdata")
        os.makedirs(datadir, exist_ok=True)
        self.testpath = os.path.join(datadir, self.testfile)
        df.to_csv(self.testpath, index=False)
        # Lag en kopi med navn "temperaturdata.csv"
        self.rentfile = os.path.join(datadir, "temperaturdata.csv")
        df.to_csv(self.rentfile, index=False)
        # Lag en kopi med navn "temperaturdata_feilverdier.csv"
        self.feilfile = os.path.join(datadir, "temperaturdata_feilverdier.csv")
        df.to_csv(self.feilfile, index=False)

    def tearDown(self):
        # Rydd opp testfiler etterpå
        for f in [self.testpath, self.rentfile, self.feilfile]:
            if os.path.isfile(f):
                os.remove(f)

    def test_les_data_finner_fil(self):
        # Denne skal finne filen
        df = databehandling._les_data(self.testfile)
        self.assertIsInstance(df, pd.DataFrame)

    def test_les_data_feiler_hvis_ikke_finnes(self):
        # Denne skal kaste FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            databehandling._les_data("finnes_ikke.csv")

    def test_sjekk_manglende_verdier(self):
        # Sjekker om riktig antall manglende verdier
        missing = databehandling.sjekk_manglende_verdier_rentdatasett()
        self.assertEqual(missing, 1)

    def test_sjekk_feilverdier(self):
        feil = databehandling.sjekk_feilverdier_rentdatasett()
        # -100 og 100 skal regnes som feil
        self.assertEqual(feil, 2)

    def test_fyll_manglende_verdier(self):
        df = databehandling.fyll_manglende_verdier(self.testfile, metode="interpolasjon")
        self.assertFalse(df["temperature_2m"].isna().any())

    def test_korriger_urealistiske_verdier(self):
        df = databehandling.korriger_urealistiske_verdier(self.testfile)
        # Nå skal alle verdier være innenfor [-40, 40]
        self.assertTrue(((df["temperature_2m"] >= -40) & (df["temperature_2m"] <= 40)).all())

    def test_fyll_manglende_verdier_ugyldig_metode(self):
        with self.assertRaises(ValueError):
            databehandling.fyll_manglende_verdier(self.testfile, metode="ukjent")

if __name__ == "__main__":
    unittest.main()
