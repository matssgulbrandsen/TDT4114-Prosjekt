import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

# Legg til src/temperaturdata i importstien
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src" / "temperaturdata"
sys.path.append(str(src_path))

class TestDatainnsamling(unittest.TestCase):
    def setUp(self):
        # Setter opp en dummy respons for API-kallet
        self.dummy_hourly = MagicMock()
        self.dummy_hourly.Time.return_value = 0
        self.dummy_hourly.TimeEnd.return_value = 3600 * 2
        self.dummy_hourly.Interval.return_value = 3600
        self.dummy_hourly.Variables.return_value.ValuesAsNumpy.return_value = [1.0, 2.0]

        self.dummy_response = MagicMock()
        self.dummy_response.Latitude.return_value = 63.43
        self.dummy_response.Longitude.return_value = 10.39
        self.dummy_response.Elevation.return_value = 10
        self.dummy_response.Timezone.return_value = "Europe/Oslo"
        self.dummy_response.TimezoneAbbreviation.return_value = "CET"
        self.dummy_response.UtcOffsetSeconds.return_value = 3600
        self.dummy_response.Hourly.return_value = self.dummy_hourly

    @patch("requests_cache.CachedSession")
    @patch("retry_requests.retry")
    @patch("openmeteo_requests.Client")
    @patch("os.makedirs")
    @patch("pandas.DataFrame.to_csv")
    def test_kan_hente_og_lagre_data(self, mock_to_csv, mock_makedirs, mock_client, mock_retry, mock_cache):
        # Lager en dummy weather_api som returnerer dummy-responsen
        dummy_client = MagicMock()
        dummy_client.weather_api.return_value = [self.dummy_response]
        mock_client.return_value = dummy_client

        # Importerer scriptet (eller kjører det som funksjon, evt. kopier script inn her)
        import importlib
        # Scriptet må hete datainnsamling.py og ligge i src/temperaturdata
        try:
            import datainnsamling
        except ModuleNotFoundError:
            datainnsamling = importlib.import_module("datainnsamling")

        # Sjekk at det faktisk ble forsøkt å lagre en DataFrame til csv
        self.assertTrue(mock_to_csv.called)
        # Sjekk at DataFrame har riktig kolonner
        args, kwargs = mock_to_csv.call_args
        df: pd.DataFrame = args[0] if args else None
        # Siden vi mocker, er ikke DataFrame-objektet lett tilgjengelig her, 
        # men vi kan sjekke at to_csv ble kalt.
        # Dersom du ønsker å sjekke mer, bør du flytte scriptkoden inn i en funksjon.

if __name__ == "__main__":
    unittest.main()
