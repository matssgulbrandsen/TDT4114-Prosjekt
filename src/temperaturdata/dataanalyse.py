import pandas as pd
import numpy as np
from scipy.stats import pearsonr

DATAFIL = "../data/temperaturdata/temperaturdata.csv"


def _les_data():
    """
    Leser inn temperaturdata fra standard filsti og gjør klar DataFrame.
    Trekker også ut årstall fra 'date'-kolonnen.
    """
    df = pd.read_csv(DATAFIL)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    return df

def statistikk_per_aar():
    """
    Beregner gjennomsnitt, median og standardavvik per år for temperaturdataen.
    Returnerer en DataFrame med år, gjennomsnitt, median og standardavvik.
    """
    df = _les_data()
    grupper = df.groupby('year')['temperature_2m'].agg(
        gjennomsnitt='mean',
        median='median',
        stdavvik='std'
    ).reset_index()
    return grupper

def beskriv_data():
    """
    Returnerer Pandas describe() statistikk for temperaturkolonnen.
    """
    df = _les_data()
    return df['temperature_2m'].describe()

def fjern_ekstreme_verdier(lav_percentil=0.01, hoy_percentil=0.99):
    """
    Fjerner ekstreme verdier (outliers) fra temperaturdataen basert på percentiler.
    Returnerer en renset DataFrame.
    """
    df = _les_data()
    lav = df['temperature_2m'].quantile(lav_percentil)
    hoy = df['temperature_2m'].quantile(hoy_percentil)
    df_renset = df[(df['temperature_2m'] >= lav) & (df['temperature_2m'] <= hoy)]
    return df_renset


def pearson_korrelasjon():
    """
    Beregner Pearson korrelasjon mellom temperatur og år.
    Returnerer en DataFrame med korrelasjonsverdier.
    """
    df = _les_data()
    x = df['year']
    y = df['temperature_2m']
    mask = ~np.isnan(y)
    x = x[mask]
    y = y[mask]
    r, p = pearsonr(x, y)
    print(f"Pearson korrelasjon mellom år og temperatur: r = {r:.4f}, p-verdi = {p:.4f}")
    return r, p