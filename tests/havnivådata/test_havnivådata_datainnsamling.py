import unittest
import sys
import pandas as pd
from pathlib import Path
import builtins

# Legg til src/Havnådata i path
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "Havnivådata"
sys.path.append(str(src_path))

from Datainnsamling import (
    hent_metadata_og_lagre,
    filtrer_ssh_metadata,
    ssh_datasets_listcomp,
    filtrer_ssh_datasets_sql,
    last_ned_nasa_ssh_data
)

class TestDatainnsamling(unittest.TestCase):
    def setUp(self):
        # Arrange: Sett opp prosjekt- og filstier, og undertrykk print
        self.data_dir = project_root / "data" / "Havnivådata"
        self.metadata_path = self.data_dir / "metadata_datasetliste.json"
        self.original_print = builtins.print
        builtins.print = lambda *args, **kwargs: None

    def tearDown(self):
        # Tilbakestill print etter hver test
        builtins.print = self.original_print

    def test_hent_metadata_og_lagrer_korrekt(self):
        # Act
        df = hent_metadata_og_lagre()

        # Assert
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertTrue(self.metadata_path.exists())

    def test_filtrer_ssh_metadata_gir_filtrert_resultat(self):
        # Arrange
        hent_metadata_og_lagre()

        # Act
        df = filtrer_ssh_metadata(terskel=10000)

        # Assert
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("SSH", df["title"].iloc[0])
        self.assertGreaterEqual(df["tileCount"].iloc[0], 10000)

    def test_ssh_datasets_listcomp_returnerer_filtrert_df(self):
        # Arrange
        hent_metadata_og_lagre()

        # Act
        df = ssh_datasets_listcomp(str(self.metadata_path), terskel=10000)

        # Assert
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue((df["tileCount"] >= 10000).all())
        self.assertTrue(df["title"].str.contains("SSH", case=False).all())

    def test_filtrer_ssh_datasets_sql_returnerer_korrekt(self):
        # Arrange
        hent_metadata_og_lagre()

        # Act
        df = filtrer_ssh_datasets_sql(str(self.metadata_path), terskel=10000)

        # Assert
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue((df["tileCount"] >= 10000).all())
        self.assertTrue(df["title"].str.contains("SSH", case=False).all())

    def test_last_ned_nasa_ssh_data_returnerer_dataframe(self):
        # Act
        df = last_ned_nasa_ssh_data()

        # Assert
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertIn("mean", df.columns)

    def test_last_ned_nasa_ssh_data_feiler_med_feil_dataset(self):
        # Act
        df = last_ned_nasa_ssh_data(ds_navn="FEIL_NAVN")

        # Assert: Forvent None ved feil input
        self.assertIsNone(df, "Ved feil datasett skal funksjonen returnere None")

if __name__ == '__main__':
    unittest.main()
