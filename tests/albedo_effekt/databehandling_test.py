"""
Enhetstester for src/albedo_effekt/databehandling.py
2 positive og 2 negative tester for de viktigste funksjonene
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from albedo_effekt import databehandling

class TestAlbedoDatabehandling(unittest.TestCase):
    """
    Tester for viktigste funksjoner i databehandling.py
    """

    def setUp(self):
        """
        Oppretter dummy csv-folder og en enkel test-csv for bruk i tester
        """
        self.dummy_csv_folder = "dummy_csv"
        os.makedirs(self.dummy_csv_folder, exist_ok=True)
        df = pd.DataFrame({"lat": [1], "lon": [2], "AL-BB-DH-ERR": [0.001], "AL-BB-DH": [0.4], "quality_flag": [1]})
        df.to_csv(os.path.join(self.dummy_csv_folder, "Albedo effekt 2004.csv"), index=False)

    def tearDown(self):
        """
        Sletter dummy-folder og filer etter hver test
        """
        for fil in os.listdir(self.dummy_csv_folder):
            os.remove(os.path.join(self.dummy_csv_folder, fil))
        os.rmdir(self.dummy_csv_folder)
        if os.path.exists("lavfeil.csv"):
            os.remove("lavfeil.csv")

    def test_dann_lavfeilmargin_fil_positiv(self):
        """
        Positiv test
        danner lavfeilmargin-fil fra gyldig dummy-data
        """
        output = "lavfeil.csv"
        try:
            databehandling.dann_lavfeilmargin_fil(
                csv_folder=self.dummy_csv_folder,
                aar_liste=[2004],
                output_file=output,
                feilmargin=0.01
            )
            self.assertTrue(os.path.exists(output))
        finally:
            if os.path.exists(output):
                os.remove(output)

    def test_dann_lavfeilmargin_fil_mangler_fil(self):
        """
        Negativ test
        forventer FileNotFoundError når input-fil ikke finnes
        """
        with self.assertRaises(FileNotFoundError):
            databehandling.dann_lavfeilmargin_fil(
                csv_folder=self.dummy_csv_folder,
                aar_liste=[2020],  # Denne finnes ikke
                output_file="skal_ikke_lages.csv",
                feilmargin=0.01
            )


    def test_relevante_filer_interpolasjon_positiv(self):
        """
        Positiv test
        lager _komplett-fil fra gyldig dummy-data
        """
        outputfolder = "dummy_out"
        os.makedirs(outputfolder, exist_ok=True)
        try:
            databehandling.relevante_filer_interpolasjon(
                folder_path=self.dummy_csv_folder,
                output=outputfolder
            )
            filer = os.listdir(outputfolder)
            self.assertTrue(any(f.endswith("_komplett.csv") for f in filer))
        finally:
            for fil in os.listdir(outputfolder):
                os.remove(os.path.join(outputfolder, fil))
            os.rmdir(outputfolder)

    def test_relevante_filer_interpolasjon_tom_folder(self):
        """
        Negativ test
        tomt input-folder, skal ikke kaste unntak eller lage filer
        """
        emptyfolder = "empty_csv"
        os.makedirs(emptyfolder, exist_ok=True)
        try:
            databehandling.relevante_filer_interpolasjon(
                folder_path=emptyfolder,
                output=emptyfolder
            )
            self.assertEqual(os.listdir(emptyfolder), [])
        finally:
            os.rmdir(emptyfolder)

if __name__ == "__main__":
    unittest.main()
