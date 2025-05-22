"""
Hovedfokus i denne modulen er å hente og utforske albedo-data fra EUMETSAT. 
Filene lagres med originalnavn for gjenbruk.

Denne filen demonstrerer:
  1. last_alle_netcdf_filer() – laster ned år 2004–2024 for 25. juni
  2. vis_variable_long_names() – lister variabler og deres long_name for tolkning/kvalitet
  3. query_albedo_i_omraade() – teller punkter i et indeks-område kun basert på AL-BB-DH-ERR (med Pandas SQL)
  4. ploter_albedo_med_lav_error_verdier() – visualiserer alle gode datapunkter i valgt område
  5. utforsk_albedo_data(download_all=True) – kjører de øvrige funksjonene i rekkefølge for å demonstrere datainnsamling og utforskning

Hovedrapporten er i Jupyter Notebook-format og inneholder output og tolkning av output.
"""

import os
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import netCDF4
import xarray as xr
import pandas as pd
import pandasql as ps
import matplotlib.pyplot as plt
import numpy as np

# Felles konstanter for datainnsamling
USERNAME = 'matsgulbrandsen'
PASSWORD = 'V2.ShXbmWRZ!S9a'
BASE_URL = "https://datalsasaf.lsasvcs.ipma.pt/PRODUCTS/MSG/MTALv2/NETCDF"
DATA_FOLDER = os.path.join("..", "data", "albedo_effekt_data","netcdf")


def last_alle_netcdf_filer():
    """
    Laster ned NetCDF4-filer for 25. juni hvert år fra 2004 til 2024,
    og lagrer dem i data folder.
    """
    os.makedirs(DATA_FOLDER, exist_ok=True)
    # For løkke for å iterere nedlastningen for år fra 2004 til 2024
    for year in range(2004, 2025):
        dato = datetime(year, 6, 25)
        fn = dato.strftime("%Y%m%d0000")
        file_name = f"NETCDF4_LSASAF_MSG_ALBEDO-D10v2_MSG-Disk_{fn}.nc"
        url = f"{BASE_URL}/{dato.strftime('%Y/%m/%d')}/{file_name}"
        dst = os.path.join(DATA_FOLDER, file_name)

        if not os.path.exists(dst):
            print(f"🔽 Laster ned {file_name} …")
            try:
                r = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=30)
                r.raise_for_status()
            except requests.RequestException as e:
                print(f"   ❌ Feil ved nedlasting: {e}")
                continue
            try:
                with open(dst, 'wb') as f:
                    f.write(r.content)
                print(f"   ✔ Lagret: {file_name}")
            except Exception as e:
                print(f"   ❌ Klarte ikke lagre {file_name}: {e}")
        else:
            print(f"✔ Allerede lastet ned: {file_name}")


def vis_variable_long_names(filsti):
    """
    Skriver ut én linje per variabel på format:
         <variabelnavn>: <long_name>
    Hopper over variabler uten long_name.
    Robust: Rapporterer feil om fil ikke finnes eller ikke kan leses og koden stopper ikke.
    """
    if not os.path.exists(filsti):
        print(f"❌ Filen finnes ikke: {filsti}")
        return
    try:
        with netCDF4.Dataset(filsti, 'r') as ds:
            for name, var in ds.variables.items():
                if "long_name" in var.ncattrs():
                    print(f"{name}: {var.getncattr('long_name')}")
    except Exception as e:
        print(f"❌ Feil ved lesing av NetCDF-fil: {e}")



def query_albedo_i_omraade(
    filsti,
    lat_min,
    lat_max,
    lon_min,
    lon_max,
    max_error=0.01
):
    """
    Teller antall punkter i indeks-området
    lat[min:max], lon[min:max]
    hvor AL-BB-DH-ERR < max_error(0.1).
    Robust: Sjekker parameterverdier og håndterer feil.
    """
    if not os.path.exists(filsti):
        print(f"❌ Fant ikke fil: {filsti}")
        return
    if not (0 <= lat_min < lat_max and 0 <= lon_min < lon_max):
        print("❌ Ugyldige indeksverdier for område!")
        return
    try:
        ds = xr.open_dataset(filsti)
        # Sjekk at variabel finnes:
        if "AL-BB-DH-ERR" not in ds:
            print("❌ Variabelen 'AL-BB-DH-ERR' finnes ikke i datasettet!")
            return
        ds_sel = ds.isel(
            lat=slice(lat_min, lat_max),
            lon=slice(lon_min, lon_max)
        )
        df = ds_sel[["AL-BB-DH-ERR"]].to_dataframe().reset_index()
        q = f"""
        SELECT lat, lon
          FROM df
         WHERE `AL-BB-DH-ERR` < {max_error}
        """
        res = ps.sqldf(q, locals(), db_uri="sqlite:///:memory:") # Bruker sqlite memmory for å forhindre transaksjonsfeil i Jupyter/interaktive miljøer
        count = len(res)
        print(f"\n Punkter med ERR<{max_error} i indeks-område "
              f"lat[{lat_min}:{lat_max}], lon[{lon_min}:{lon_max}]: {count}")
    except Exception as e:
        print(f"❌ Feil under spørring/innlesing: {e}")



def plot_albedo_with_low_error_points(
    filename: str,
    albedo_var: str = "AL-BB-DH",
    error_var: str = "AL-BB-DH-ERR",
    lat_min: int = 650,
    lat_max: int = 700,
    lon_min: int = 1700,
    lon_max: int = 1800,
    max_error: float = 0.01
):
    """
    Visualiserer albedo i angitt område, og markerer ALLE piksler med lav feilmargin (< max_error)
    med grønne punkter.
    """
    nc_path = os.path.join(DATA_FOLDER, filename)
    ds = xr.open_dataset(nc_path)
    alb = ds[albedo_var].isel(
        time=0,
        lat=slice(lat_min, lat_max),
        lon=slice(lon_min, lon_max)
    ).values
    err = ds[error_var].isel(
        time=0,
        lat=slice(lat_min, lat_max),
        lon=slice(lon_min, lon_max)
    ).values

    # Maske for piksler med lav feilmargin
    low_err_mask = (err < max_error)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(alb, origin="upper", interpolation="none", cmap="viridis")
    plt.colorbar(im, ax=ax, label="Albedo-verdi")

    # Marker ALLE piksler med lav feilmargin som grønne punkter
    y, x = np.where(low_err_mask)
    ax.scatter(x, y, color="lime", s=8, marker='o', label=f"Error < {max_error}")

    ax.set_title(
        f"{albedo_var} med punkter for feilmargin < {max_error}\n"
        f"(lat idx {lat_min}:{lat_max}, lon idx {lon_min}:{lon_max})"
    )
    ax.set_xlabel("Lon-indeks")
    ax.set_ylabel("Lat-indeks")
    ax.legend()
    plt.tight_layout()
    plt.show()


def utforsk_albedo_data():
    """
    Hovedfunksjon for Oppgave 2.
    Kjører alle steg: nedlasting, variabelstruktur, SQL-filtrering og visualisering.
    """
    print("OPPGAVE 2: Datainnsamling og Utforskning")

    
    print("\n1.Nedlasting")
    last_alle_netcdf_filer()

    eksempel = "NETCDF4_LSASAF_MSG_ALBEDO-D10v2_MSG-Disk_200406250000.nc"
    filsti = os.path.join(DATA_FOLDER, eksempel)
    if not os.path.exists(filsti):
        print(f"❗ Fant ikke eksempel-fil: {eksempel}")
        return

    print("\n2.Vis variabler og long_name")
    vis_variable_long_names(filsti)

    print("\n3.SQL-query i område (kun AL-BB-DH-ERR)")
    query_albedo_i_omraade(
        filsti,
        650,   # lat_min
        700,   # lat_max
        1700,  # lon_min
        1800,  # lon_max
        max_error=0.01
    )

    print("\n4.Visualiser albedo og gode punkter")
    plot_albedo_with_low_error_points(
        filename=eksempel,
        lat_min=650,
        lat_max=700,
        lon_min=1700,
        lon_max=1800,
        max_error=0.01
    )


if __name__ == "__main__":
    utforsk_albedo_data()

