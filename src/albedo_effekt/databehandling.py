import os
import xarray as xr
import pandas as pd
import pandasql as psql
import numpy as np
import glob


def trekk_ut_albedo_csv(y_min, y_max, x_min, x_max, start_aar, slutt_aar, ncdf_folder, csv_folder):
    """
    Trekker ut nødvendige data fra NetCDF-filer til CSV for hvert år.
    """
    os.makedirs(csv_folder, exist_ok=True)
    for year in range(start_aar, slutt_aar + 1):
        file_name = f"NETCDF4_LSASAF_MSG_ALBEDO-D10v2_MSG-Disk_{year}06250000.nc"
        file_path = os.path.join(ncdf_folder, file_name)
        if not os.path.exists(file_path):
            print(f"Filen finnes ikke: {file_path}")
            continue
        ds = xr.open_dataset(file_path)
        ds_utsnitt = ds.isel(lat=slice(y_min, y_max), lon=slice(x_min, x_max))
        variables = ["AL-BB-DH", "AL-BB-DH-ERR", "quality_flag"]
        df = ds_utsnitt[variables].to_dataframe().reset_index()
        csv_file_name = f"Albedo effekt {year}.csv"
        csv_file_path = os.path.join(csv_folder, csv_file_name)
        df.to_csv(csv_file_path, index=False)
        print(f"Data for {year} lagret som {csv_file_path}")

def dann_lavfeilmargin_fil(csv_folder, aar_liste, output_file, feilmargin=0.01):
    """
    Finner koordinater med lav feilmargin (<feilmargin) i alle år og lagrer disse til output_file.
    """
    def fetch_filtered_coords(file_path):
        df = pd.read_csv(file_path)
        query = f"""
        SELECT lat, lon
        FROM df
        WHERE `AL-BB-DH-ERR` < {feilmargin}
        """
        result = psql.sqldf(query, locals())
        return set(zip(result["lat"], result["lon"]))

    qualified_coords = None
    for year in aar_liste:
        file_path = os.path.join(csv_folder, f"Albedo effekt {year}.csv")
        coords = fetch_filtered_coords(file_path)
        print(f"{year}: {len(coords)} områder med feil < {feilmargin}")
        qualified_coords = coords if qualified_coords is None else qualified_coords.intersection(coords)

    print(f"\nTotalt antall områder med feil < {feilmargin} i alle år: {len(qualified_coords)}")
    df_result = pd.DataFrame(list(qualified_coords), columns=["lat", "lon"])
    df_result.to_csv(output_file, index=False)
    print(f"Koordinatene med best data lagret i {output_file}")

def relevante_filer_interpolasjon(folder_path,output, suffix="_komplett.csv"):
    relevante_filer = [f"Albedo effekt {year}.csv" for year in range(2004, 2025)]
    for file in os.listdir(folder_path):
        if file in relevante_filer:
            path = os.path.join(folder_path, file)
            df = pd.read_csv(path)
            if "AL-BB-DH" in df.columns:
                antall_før = len(df)

                # Bytt ut -1 med NaN i AL-BB-DH
                df["AL-BB-DH"] = df["AL-BB-DH"].replace(-1, np.nan)

                # Sett ugyldige verdier (<0 eller >1) til NaN
                mask_ugyldig = (df["AL-BB-DH"] < 0) | (df["AL-BB-DH"] > 1)
                ant_ugyldige = mask_ugyldig.sum()
                df.loc[mask_ugyldig, "AL-BB-DH"] = np.nan

                ant_nan = df["AL-BB-DH"].isnull().sum()

                # Interpolasjon
                df["AL-BB-DH"] = df["AL-BB-DH"].interpolate(method="linear", limit_direction="both")

                ant_nan_etter = df["AL-BB-DH"].isnull().sum()
                antall_etter = len(df)
                ny_fil = file.replace(".csv", suffix)
                df.to_csv(os.path.join(output, ny_fil), index=False)
                print(
                    f"{file}: {ant_ugyldige} ugyldige (<0/>1) ble satt til NaN. "
                    f"{ant_nan} manglende (-1/NaN) før, {ant_nan_etter} etter interpolasjon. "
                    f"Rader: {antall_før} → {antall_etter}. Ny fil: {ny_fil}"
                )
            else:
                print(f"{file}: AL-BB-DH finnes ikke, ingen endring.")




def albedo_behandling():
    """
    Kjører hele albedo-databehandling.py en gang.
    - Trekker ut CSV fra NetCDF hvis nødvendig.
    - Lager og evt. interpolerer lavfeilmargin-fil.
    - Gjør ikke noe hvis ferdig interpolert fil allerede finnes.
    """

    # Finn prosjektroten (der 'data' ligger)
    # Fungerer både om du kjører fra notebook eller src
    cwd = os.getcwd()
    prosjektrot = cwd
    while not os.path.isdir(os.path.join(prosjektrot, "data")) and prosjektrot != os.path.dirname(prosjektrot):
        prosjektrot = os.path.dirname(prosjektrot)
    if not os.path.isdir(os.path.join(prosjektrot, "data")):
        raise FileNotFoundError("Fant ikke 'data'-mappen i prosjektet. Sjekk prosjektstruktur.")

    # Sett mapper
    data_base = os.path.join(prosjektrot, "data", "albedo_effekt_data")
    ncdf_folder = os.path.join(data_base, "netcdf")
    csv_folder = os.path.join(data_base, "csv_albedo_effekt")
    csv_folder_komplett = os.path.join(data_base, "csv_albedo_effekt_komplett")
    os.makedirs(csv_folder, exist_ok=True)

    # Parametre
    y_min, y_max = 650, 700
    x_min, x_max = 1700, 1800
    start_aar, slutt_aar = 2004, 2024
    aar_liste = list(range(start_aar, slutt_aar + 1))
    output_file = os.path.join(csv_folder, "data_m-lavfeilmargin.csv")
    komplett_file = output_file.replace(".csv", "_komplett.csv")

    # Sjekk om _komplett-fil finnes
    if os.path.exists(komplett_file):
        print(f"✅ Ferdig interpolert lavfeilmargin-fil finnes: {os.path.basename(komplett_file)} – hopper over prosessering.")
        return

    # 1. Lag CSV-filene fra NetCDF (kun hvis det ikke finnes ferdige CSV-er)
    if not glob.glob(os.path.join(csv_folder, "Albedo*csv")):
        print("🔄 Trekker ut CSV fra NetCDF...")
        trekk_ut_albedo_csv(y_min, y_max, x_min, x_max, start_aar, slutt_aar, ncdf_folder, csv_folder)
    else:
        print("✅ CSV-filer finnes fra før – hopper over ekstraksjon.")

    # 2. Lag lavfeilmargin-fil hvis nødvendig
    if not os.path.exists(output_file):
        print("🔄 Lager lavfeilmargin-fil...")
        dann_lavfeilmargin_fil(csv_folder, aar_liste, output_file)
    else:
        print("✅ Lavfeilmargin-fil finnes – sjekker kvalitet/interpolasjon.")

    # 3. Interpolasjon – kun om _komplett ikke finnes
    print("🔍 Sjekker/utfører interpolasjon på lavfeilmargin-fil om nødvendig...")
    relevante_filer_interpolasjon(csv_folder,csv_folder_komplett)
