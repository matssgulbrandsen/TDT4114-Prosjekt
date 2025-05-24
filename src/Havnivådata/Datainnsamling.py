import requests
import pandas as pd
from pathlib import Path

def hent_metadata_og_lagre():
    """
    Henter metadata for tilgjengelige datasett fra NASA sin API.
    Velger ut relevante kolonner, og lagrer resultatet som en JSON-fil i
    data/Havnivådata-mappe.

    Funksjonen:
    - Laster ned datasett-metadata fra sealevel-nexus.jpl.nasa.gov.
    - Velger ut kun kolonnene: 'title', 'tileCount', 'iso_start', 'iso_end'.
    - Lagrer metadata som JSON-fil på riktig sted i prosjektmappen.
    - Skriver ut antall datasett og en tabell i konsoll for rask oversikt.

    Returnerer:
        pd.DataFrame: DataFrame med metadata for alle datasettene.
    """
    # Hent data fra API 
    base_url = "https://sealevel-nexus.jpl.nasa.gov"
    endpoint = "/list"
    url = base_url + endpoint

    resp = requests.get(url)
    resp.raise_for_status()          # feiler tidlig om noe går galt
    data = resp.json()
    df   = pd.DataFrame(data)

    # Velg ønskede kolonner 
    ønskede = ["title", "tileCount", "iso_start", "iso_end"]
    df = df[ønskede]

    print(f"✅ Antall datasett hentet: {len(df)}")
    print(f"📊 Kolonner: {df.columns.tolist()}")

    # Finn prosjektrot
    project_root = Path(__file__).resolve().parents[2]

    # Lag underkatalogen data/Havnivådata og skriv JSON dit
    data_dir = project_root / "data" / "Havnivådata"
    data_dir.mkdir(parents=True, exist_ok=True)

    output_path = data_dir / "metadata_datasetliste.json"
    df.to_json(output_path, orient="records", lines=True)
    print(f"✅ Metadata lagret som JSON i: {output_path}")

    # Vis tabell for å gi rask oversikt
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

    print("\n📋 Datasett-tabell:")
    print(df.to_string(index=False))

    return df


def filtrer_ssh_metadata(terskel: int = 10000) -> pd.DataFrame:
    """
    Leser fra data/Havnivådata/metadata_datasetliste.json,
    filtrerer bort alle oppføringer med tileCount < terskel,
    og beholder kun de radene hvor 'title' inneholder 'SSH'.
    Returnerer en reset-index DataFrame.
    """
    import pandas as pd
    from pathlib import Path

    # Finn metadata-fila i data/Havnivådata/
    project_root  = Path(__file__).resolve().parents[2]
    metadata_path = project_root / "data" / "Havnivådata" / "metadata_datasetliste.json"

    # Les JSON 
    df = pd.read_json(metadata_path, orient="records", lines=True)

    # Filtrer etter datamengde
    df = df[df["tileCount"] >= terskel]

    # Filtrer på 'SSH' i title
    mask   = df["title"].str.contains("SSH", case=False, na=False)
    df_ssh = df[mask].reset_index(drop=True)

    return df_ssh


def ssh_datasets_listcomp(metadata_path: str, terskel: int = 10000) -> pd.DataFrame:
    """
    Leser metadata fra en JSON-fil, og returnerer en DataFrame
    med bare de radene der 'title' inneholder 'SSH' og 'tileCount' er over terskel, ved hjelp av list comprehension.
    
    Returnerer:
        pd.DataFrame: Filtrert DataFrame med sammenhengende index.
    """
    # Les inn alle rader som dict-liste
    records = pd.read_json(metadata_path, orient="records", lines=True).to_dict("records")
    
    # Bruker list comprehension for å filtrere
    filtered = [
        record for record in records
        if ("SSH" in str(record.get("title", "")).upper()) and (record.get("tileCount", 0) >= terskel)
    ]
    
    # Lag DataFrame fra den filtrerte listen
    df_ssh = pd.DataFrame(filtered).reset_index(drop=True)
    return df_ssh



def filtrer_ssh_datasets_sql(metadata_path: str, terskel: int = 10000) -> pd.DataFrame:
    """
    Leser metadata fra en JSON-fil og returnerer en DataFrame
    med kun radene der 'title' inneholder 'SSH' og 'tileCount' er over terskel, ved bruk av pandasql.

    Returnerer:
        pd.DataFrame: Filtrert DataFrame med sammenhengende index.
    """
    from pandasql import sqldf

    # Les inn alle rader til DataFrame
    df = pd.read_json(metadata_path, orient="records", lines=True)

    # Lag en SQL-spørring ('SSH' i title)
    query = f"""
        SELECT *
        FROM df
        WHERE UPPER(title) LIKE '%SSH%'
          AND tileCount >= {terskel}
    """
    # Kjør SQL-spørringen med sqldf
    df_ssh = sqldf(query, locals()).reset_index(drop=True)
    return df_ssh

def last_ned_nasa_ssh_data(
    ds_navn: str = "NASA_SSH_REF_SIMPLE_GRID_V1_Monthly",
    bbox: str = "-180.0,-90.0,180.0,90.0",
    start: str = "1992-01-01T00:00:00Z",
    slutt: str = "2025-01-01T00:00:00Z",
    filnavn: str = "havnivaadata.json"
) -> pd.DataFrame:
    """
    Laster ned SSH datasett fra NASA Sealevel Nexus API og lagrer det som JSON.
    Returnerer en DataFrame med ønskede kolonner.

    Returnerer:
        pd.DataFrame: DataFrame med de viktigste statistikk-kolonnene for videre analyse
    """
    # Hent dataen fra API
    base_url = "https://sealevel-nexus.jpl.nasa.gov"
    endpoint = "/timeSeriesSpark"
    url = base_url + endpoint

    params = {
        "ds": ds_navn,
        "b": bbox,
        "startTime": start,
        "endTime": slutt,
        "output": "JSON"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        ts_data = response.json()
    else:
        print("❌ Feil ved henting av data:", response.status_code, response.text)
        return None

    # Bearbeider rådata og lager DataFrame
    if ts_data and "data" in ts_data:
        data_list_of_lists = ts_data["data"]
        all_records = [record for sublist in data_list_of_lists for record in sublist]
        df = pd.DataFrame(all_records)

        ønskede_kolonner = {"min", "max", "mean", "cnt", "std", "time", "iso_time"}
        tilgjengelige_kolonner = [col for col in ønskede_kolonner if col in df.columns]
        df = df[tilgjengelige_kolonner]

        # Lagres på riktig sted
        project_root = Path(__file__).resolve().parents[2]

        data_dir = project_root / "data" / "Havnivådata"
        data_dir.mkdir(parents=True, exist_ok=True)

        output_path = data_dir / "havnivaadata.json"
        json_path = data_dir / "havnivaadata.json"
        df.to_json(json_path, orient="records", lines=True)

        print(f"✅ Data lagret i: {json_path}")

        return df
    else:
        print("❌ Responsen har ikke forventet struktur eller er tom.")
        return None
