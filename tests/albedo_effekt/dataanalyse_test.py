"""
Enhetstester for src/albedo_effekt/databehandling.py
2 positive og 2 negative tester for de viktigste funksjonene
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import unittest
import pandas as pd
import numpy as np
from albedo_effekt.dataanalyse import beregn_albedo_statistikk

class TestBeregnAlbedoStatistikk(unittest.TestCase):
    """
    Tester for viktigste funksjoner i dataanalyse.py
    """

    def tearDown(self):
        """
        Slett midlertidige testfiler etter hver test
        """
        for f in ["ref.csv", "data.csv"]:
            if os.path.exists(f):
                os.remove(f)

    def test_to_punkter(self):
        """
        Positiv test 
        to felles punkter, sjekker verdier
        """
        ref = pd.DataFrame({'lat': [1, 2], 'lon': [10, 20]})
        data = pd.DataFrame({'lat': [1, 2], 'lon': [10, 20], 'AL-BB-DH': [0.4, 0.6]})
        ref.to_csv("ref.csv", index=False)
        data.to_csv("data.csv", index=False)
        mat, år, gj, med, std = beregn_albedo_statistikk("ref.csv", "data.csv", print_matrise=False)
        self.assertAlmostEqual(gj[0], 0.5)
        self.assertAlmostEqual(med[0], 0.5)
        self.assertAlmostEqual(std[0], np.std([0.4, 0.6], ddof=1))

    def test_ett_punkt(self):
        """
        Positiv test
        ett felles punkt
        """
        ref = pd.DataFrame({'lat': [1], 'lon': [10]})
        data = pd.DataFrame({'lat': [1], 'lon': [10], 'AL-BB-DH': [0.8]})
        ref.to_csv("ref.csv", index=False)
        data.to_csv("data.csv", index=False)
        mat, år, gj, med, std = beregn_albedo_statistikk("ref.csv", "data.csv", print_matrise=False)
        self.assertAlmostEqual(gj[0], 0.8)
        self.assertAlmostEqual(med[0], 0.8)
        self.assertTrue(np.isnan(std[0]))

    def test_ingen_felles(self):
        """
        Negativ test
        ingen felles punkter, skal gi nan
        """
        ref = pd.DataFrame({'lat': [9], 'lon': [19]})
        data = pd.DataFrame({'lat': [1], 'lon': [10], 'AL-BB-DH': [0.5]})
        ref.to_csv("ref.csv", index=False)
        data.to_csv("data.csv", index=False)
        mat, år, gj, med, std = beregn_albedo_statistikk("ref.csv", "data.csv", print_matrise=False)
        self.assertTrue(np.isnan(gj[0]))
        self.assertTrue(np.isnan(med[0]))
        self.assertTrue(np.isnan(std[0]))

    def test_mangler_kolonne(self):
        """
        Negativ test
        data mangler AL-BB-DH, skal gi nan
        """
        ref = pd.DataFrame({'lat': [1], 'lon': [10]})
        data = pd.DataFrame({'lat': [1], 'lon': [10]}) # Ingen AL-BB-DH kolonne til høyre
        ref.to_csv("ref.csv", index=False)
        data.to_csv("data.csv", index=False)
        mat, år, gj, med, std = beregn_albedo_statistikk("ref.csv", "data.csv", print_matrise=False)
        self.assertTrue(np.isnan(gj[0]))
        self.assertTrue(np.isnan(med[0]))
        self.assertTrue(np.isnan(std[0]))

if __name__ == "__main__":
    unittest.main()
