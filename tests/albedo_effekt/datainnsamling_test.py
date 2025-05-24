"""
Enhetstester for src/albedo_effekt/datainnsamling.py
2 positive og 2 negative tester for de viktigste funksjonene
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import unittest

from albedo_effekt import datainnsamling  # Endre til navnet på modulen din hvis nødvendig

class TestAlbedodatainnsamling(unittest.TestCase):
    def setUp(self):
        '''
        Opprett en dummy-fil for testing
        '''
        self.testfile = "dummy.nc"
        with open(self.testfile, "w") as f:
            f.write("Dette er ikke en gyldig netcdf-fil, men brukes for å teste eksistens.")
    
    def tearDown(self):
        if os.path.exists(self.testfile):
            os.remove(self.testfile)

    def test_vis_variable_long_names_file_exists(self):
        '''
        Positiv test
        selv om filen ikke er en gyldig netcdf-fil, skal funksjonen ikke kræsje

        '''
        try:
            datainnsamling.vis_variable_long_names(self.testfile)
        except Exception:
            self.fail("vis_variable_long_names() kastet unntak på eksisterende fil")

    def test_vis_variable_long_names_missing_file(self):
        '''
        Negativ test
        med ikke eksisterende fil skal funksjonen ikke kræsje
        '''
        try:
            datainnsamling.vis_variable_long_names("finnes_ikke.nc")
        except Exception:
            self.fail("vis_variable_long_names() kastet unntak på manglende fil")

    def test_query_albedo_i_omraade_file_exists(self):
        '''
        Positiv test
        selv om filen ikke er en gyldig netcdf-fil, skal funksjonen ikke kræsje
        '''
        try:
            datainnsamling.query_albedo_i_omraade(
                self.testfile, 0, 1, 0, 1, max_error=0.01
            )
        except Exception:
            self.fail("query_albedo_i_omraade() kastet unntak på eksisterende fil")

    def test_query_albedo_i_omraade_invalid_indices(self):
        '''
        Negativ test
        selv om filen har ugyldige indeksverdier skal funksjonen ikke kræsje
        '''
        try:
            datainnsamling.query_albedo_i_omraade(
                self.testfile, 5, 1, 0, 1, max_error=0.01
            )
        except Exception:
            self.fail("query_albedo_i_omraade() kastet unntak på ugyldige indekser")

if __name__ == "__main__":
    unittest.main()
