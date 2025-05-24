import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
import unittest
import pandas as pd
from albedo_effekt.dataprediksjon import PrediksjonVisualisering

class TestPrediksjonVisualisering(unittest.TestCase):

    def test_beregn_prediksjonsmodell_positiv(self):
        '''
          Positiv test
          Sjekker at vi får riktige kolonner og ingen manglende verdier
        '''
        predvis = PrediksjonVisualisering()
        stats = pd.DataFrame({
            "År": [2018, 2019, 2020, 2021, 2022],
            "Gjennomsnittlig albedo": [0.5, 0.52, 0.48, 0.51, 0.50]
        })
        stats, framtid, model = predvis.beregn_prediksjonsmodell(stats, antall_fremtid=2)
        self.assertIn("År", framtid.columns)
        self.assertIn("Predikert", framtid.columns)
        self.assertEqual(len(framtid), 2)
        self.assertFalse(framtid["Predikert"].isnull().any())

    def test_beregn_prediksjonsmodell_negativ(self):
        '''
        Negativ test
        Forventer FileNotFoundError hvis stats er None
        '''
        predvis = PrediksjonVisualisering()
        with self.assertRaises(FileNotFoundError):
            predvis.beregn_prediksjonsmodell(stats=None, antall_fremtid=1)

if __name__ == "__main__":
    unittest.main()
