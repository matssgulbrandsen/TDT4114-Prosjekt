import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import unittest
import numpy as np
from albedo_effekt.datavisualisering import Visualisering

class TestVisualisering(unittest.TestCase):
    def setUp(self):
        """
        Setter opp testdata
        """
        self.vis = Visualisering()
        self.årstall = [2000, 2001, 2002]
        self.gjennomsnitt = [0.5, 0.6, 0.7]
        self.median = [0.5, 0.6, 0.7]
        self.std = [0.01, 0.02, 0.03]

    def test_plot_albedo_med_std_simple(self):
        """
        Positiv test
        Sjekker at plot_albedo_med_std kjører uten feil med testdata.
        """
        
        self.vis.plot_albedo_med_std(
                self.årstall,
                self.gjennomsnitt,
                self.median,
                self.std,
                vis_plot=False 
            )

    def test_plot_albedo_med_std_negative_length(self):
        """
        Negativ test
        Sjekker at plot_albedo_med_std kaster ValueError hvis lengden på median ikke stemmer
        """
        with self.assertRaises(ValueError):
            self.vis.plot_albedo_med_std(
                self.årstall,
                self.gjennomsnitt,
                self.median[:-1],  # legger til hull i median
                self.std,
                vis_plot=False
            )

if __name__ == "__main__":
    unittest.main()
