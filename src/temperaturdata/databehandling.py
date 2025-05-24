import pandas as pd
import os


def _les_data(relativ_sti: str) -> pd.DataFrame:
    """
    Intern hjelpemetode for å lese en CSV-fil fra data/temperaturdata-mappen.
    
    Returns:
        pd.DataFrame: Innholdet i CSV-filen som DataFrame.
    """
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "temperaturdata"))
    full_path = os.path.join(base_path, relativ_sti)

    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"Finner ikke fil: {full_path}")

    return pd.read_csv(full_path)


# === 1. Manglende verdier: rent datasett ===

def sjekk_manglende_verdier_rentdatasett(kolonne: str = "temperature_2m") -> int:
    """
    Sjekker antall manglende verdier i et rent datasett uten feil.

    Datasett: 'temperaturdata.csv'

    Returns:
        int: Antall manglende verdier i kolonnen.
    """
    df = _les_data("temperaturdata.csv")

    if kolonne not in df.columns:
        raise ValueError(f"Kolonnen '{kolonne}' finnes ikke.")

    missing = df[kolonne].isna().sum()
    print(f"🧪 (Rent datasett) Manglende verdier i '{kolonne}': {missing}")
    return missing


# === 2. Manglende verdier: datasett med feil ===

def sjekk_manglende_verdier_feildatasett(kolonne: str = "temperature_2m") -> int:
    """
    Sjekker antall manglende verdier i datasettet som bevisst inneholder feil.

    Datasett: 'temperaturdata_feilverdier.csv'

    Returns:
        int: Antall manglende verdier i kolonnen.
    """
    df = _les_data("temperaturdata_feilverdier.csv")

    if kolonne not in df.columns:
        raise ValueError(f"Kolonnen '{kolonne}' finnes ikke.")

    missing = df[kolonne].isna().sum()
    print(f"🧪 (Feildatasett) Manglende verdier i '{kolonne}': {missing}")
    return missing


# === 3. Feilverdier: rent datasett ===

def sjekk_feilverdier_rentdatasett(kolonne: str = "temperature_2m", min_verdi: float = -40.0, max_verdi: float = 40.0) -> int:
    """
    Sjekker hvor mange verdier som er utenfor akseptabelt område i et rent datasett.

    Datasett: 'temperaturdata.csv'

    Returns:
        int: Antall verdier utenfor gyldig temperaturintervall.
    """
    df = _les_data("temperaturdata.csv")

    if kolonne not in df.columns:
        raise ValueError(f"Kolonnen '{kolonne}' finnes ikke.")

    feil = df[(df[kolonne] < min_verdi) | (df[kolonne] > max_verdi)]
    print(f"🚨 (Rent datasett) Feilverdier utenfor [{min_verdi}, {max_verdi}]: {len(feil)}")
    return len(feil)


# === 4. Feilverdier: datasett med feil ===

def sjekk_feilverdier_feildatasett(kolonne: str = "temperature_2m", min_verdi: float = -40.0, max_verdi: float = 40.0) -> int:
    """
    Sjekker hvor mange verdier som er utenfor akseptabelt område i datasettet med bevisste feil.

    Datasett: 'temperaturdata_feilverdier.csv'

    Returns:
        int: Antall verdier utenfor gyldig temperaturintervall.
    """
    df = _les_data("temperaturdata_feilverdier.csv")

    if kolonne not in df.columns:
        raise ValueError(f"Kolonnen '{kolonne}' finnes ikke.")

    feil = df[(df[kolonne] < min_verdi) | (df[kolonne] > max_verdi)]
    print(f"🚨 (Feildatasett) Feilverdier utenfor [{min_verdi}, {max_verdi}]: {len(feil)}")
    return len(feil)

import pandas as pd

# ------------------------------------------------------------
# ✅ FYLL INN MANGLENDE VERDIER
# ------------------------------------------------------------

def fyll_manglende_verdier(relativ_sti: str, kolonne: str = "temperature_2m", metode: str = "interpolasjon") -> pd.DataFrame:
    """
    Fyller inn manglende verdier i valgt kolonne basert på angitt metode.

    Metoder:
        - 'gjennomsnitt': fyller med gjennomsnittlig verdi
        - 'median': fyller med medianverdi
        - 'interpolasjon': lineær interpolasjon

    Returns:
        pd.DataFrame: DataFrame der manglende verdier er fylt inn.
    """
    df = _les_data(relativ_sti)

    if kolonne not in df.columns:
        raise ValueError(f"Kolonnen '{kolonne}' finnes ikke i datasettet.")

    if metode == "gjennomsnitt":
        verdi = df[kolonne].mean()
        df[kolonne] = df[kolonne].fillna(verdi)
    elif metode == "median":
        verdi = df[kolonne].median()
        df[kolonne] = df[kolonne].fillna(verdi)
    elif metode == "interpolasjon":
        df[kolonne] = df[kolonne].interpolate()
    else:
        raise ValueError("Ugyldig metode. Bruk 'gjennomsnitt', 'median' eller 'interpolasjon'.")

    print(f"🛠️ Manglende verdier i '{kolonne}' håndtert med metode: {metode}")
    return df


def korriger_urealistiske_verdier(relativ_sti: str, kolonne: str = "temperature_2m", min_val: float = -40.0, max_val: float = 40.0) -> pd.DataFrame:
    """
    Erstatter urealistiske verdier utenfor [min_val, max_val] med NaN og interpolerer.

    Eksempel: -100 eller 80 grader erstattes med lineær interpolasjon.

    Returns:
        pd.DataFrame: DataFrame der urealistiske verdier er erstattet og renset.
    """
    df = _les_data(relativ_sti)

    if kolonne not in df.columns:
        raise ValueError(f"Kolonnen '{kolonne}' finnes ikke i datasettet.")

    # Erstatter verdier utenfor gyldig intervall med None (NaN)
    df[kolonne] = [val if min_val <= val <= max_val else None for val in df[kolonne]]

    # Fyll på med lineær interpolasjon
    df[kolonne] = df[kolonne].interpolate()

    print(f"🧼 Urealistiske verdier i '{kolonne}' erstattet og interpolert innenfor [{min_val}, {max_val}]")
    return df

import matplotlib.pyplot as plt

def vis_endringer_i_data(relativ_sti: str = "temperaturdata_feilverdier.csv", kol: str = "temperature_2m"):
    """
    Leser inn datasettet, viser endringer før/etter fylling og korrigering, og visualiserer dette med grafer.
    """
    df_feil = _les_data(relativ_sti)
    df_interpolert = fyll_manglende_verdier(relativ_sti, kolonne=kol, metode="interpolasjon")
    df_korrigert = korriger_urealistiske_verdier(relativ_sti, kolonne=kol)


    # --- Visualisering av fylte manglende verdier ---
    na_mask = df_feil[kol].isna()

    plt.figure(figsize=(15,5))
    plt.plot(df_interpolert.index, df_interpolert[kol], label="Interpolert/Fylt verdi", color="tab:blue")
    plt.plot(df_feil.index, df_feil[kol], 'o', label="Original", color="tab:gray", alpha=0.5)
    plt.scatter(df_feil.index[na_mask], df_interpolert.loc[na_mask, kol], 
                color="red", label="Fylte verdier", zorder=5)
    plt.title("Visualisering av fylte manglende verdier")
    plt.xlabel("Radnummer")
    plt.ylabel("Temperatur")
    plt.legend()
    plt.show()

    # --- Visualisering av korrigerte urealistiske verdier ---
    korr_mask = (df_feil[kol] != df_korrigert[kol]) & (~df_feil[kol].isna())
    plt.figure(figsize=(15,5))
    plt.plot(df_korrigert.index, df_korrigert[kol], label="Korrigert verdi", color="tab:green")
    plt.plot(df_feil.index, df_feil[kol], 'o', label="Original", color="tab:gray", alpha=0.5)
    plt.scatter(df_feil.index[korr_mask], df_korrigert.loc[korr_mask, kol], 
                color="orange", label="Korrigerte verdier", zorder=5)
    plt.title("Visualisering av korrigerte urealistiske verdier")
    plt.xlabel("Radnummer")
    plt.ylabel("Temperatur")
    plt.legend()
    plt.show()

from IPython.display import display

def vis_endringer_med_dato(
        relativ_sti: str = "temperaturdata_feilverdier.csv", 
        kol: str = "temperature_2m",
        startdato: str = "1950-01-01 00:00"
    ):
    """
    Viser en tabell over rader som er endret (NaN fylt inn eller urealistisk verdi korrigert),
    og bruker dato/tid i stedet for radnummer. Antas timesoppløsning fra startdato.
    """
    df_feil = _les_data(relativ_sti)
    df_korrigert = korriger_urealistiske_verdier(relativ_sti, kolonne=kol)
    
    # Mask for rader med endring
    mask = (df_feil[kol].isna()) | (df_feil[kol] != df_korrigert[kol])
    
    # Lag datokolonne basert på antall rader og timesfrekvens
    datoer = pd.date_range(start=startdato, periods=len(df_feil), freq='H')
    
    # Sammenligningstabell med dato og endringer
    df_sammenligning = pd.DataFrame({
        "Dato/tid": datoer[mask],
        "Original": df_feil.loc[mask, kol].values,
        "Korrigert": df_korrigert.loc[mask, kol].values
    }).reset_index(drop=True)
    
    print("Rader med endring (med dato/tid):")
    display(df_sammenligning)

from IPython.display import display
import pandas as pd

def sammenlign_med_rent_datasett(
        feil_sti: str = "temperaturdata_feilverdier.csv",
        rent_sti: str = "temperaturdata.csv",
        kol: str = "temperature_2m",
        startdato: str = "1950-01-01 00:00"
    ):
    """
    Sammenligner korrigerte verdier med tilsvarende verdier i et rent datasett,
    viser en tabell med tidspunkt, original (feil), korrigert og 'fasit' verdi fra rent datasett.
    """
    # Les begge datasett
    df_feil = _les_data(feil_sti)
    df_korrigert = korriger_urealistiske_verdier(feil_sti, kolonne=kol)
    df_rent = _les_data(rent_sti)
    
    # Generer dato/tid-kolonne
    datoer = pd.date_range(start=startdato, periods=len(df_feil), freq='H')
    
    # Mask for rader som har fått endring
    mask = (df_feil[kol].isna()) | (df_feil[kol] != df_korrigert[kol])
    
    # Lag sammenligningstabell
    df_sammenligning = pd.DataFrame({
        "Dato/tid": datoer[mask],
        "Original (feil)": df_feil.loc[mask, kol].values,
        "Korrigert": df_korrigert.loc[mask, kol].values,
        "Rent datasett": df_rent.loc[mask, kol].values
    }).reset_index(drop=True)
    
    print("Sammenligning av korrigerte rader mot rent datasett:")
    display(df_sammenligning)
