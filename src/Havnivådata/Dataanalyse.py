import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from pathlib import Path



def beregn_korrelasjon_mnd_vs_mean(datafil: str = "../../data/Havnivådata/havnivaadata.json") -> float:
    """
    Leser havnivådata fra JSON-fil, forbereder data og beregner Pearson-korrelasjon
    mellom måneder (tidsrekkefølge) og "mean" havnivå.

    Returnerer:
        f: Pearson korrelasjonskoeffisient mellom måned og havnivå.
    """
    # Les inn data
    df = pd.read_json(datafil, orient="records", lines=True)

    # Forbered kolonner
    df["iso_time"] = pd.to_datetime(df["iso_time"])

    # Lag en kontinuerlig "måned" variabel (0, 1, 2, ..., N)
    df = df.sort_values("iso_time").reset_index(drop=True)
    df["måned_nr"] = range(len(df))

    # Beregn korrelasjon
    r, _ = pearsonr(df["måned_nr"], df["mean"])

    # Tolk resultatet
    print(f"\n Pearson korrelasjon mellom måneder og havnivåstigning: {r:.3f}")
    if r > 0.7:
        print(" Sterk positiv sammenheng! – havnivået stiger jevnt over tid.")
    elif r < -0.7:
        print(" Sterk negativ sammenheng! – havnivået synker over tid.")
    else:
        print(" Svak eller ingen tydelig sammenheng over tid.")

    #return r


def beregn_statistikk_numpy(datafil: str = "../../data/Havnivådata/havnivaadata.json") -> dict:
    """
    Beregner gjennomsnitt, median og standardavvik for 'min', 'mean' og 'max'
    ved bruk av kun NumPy (ikke Pandas-statistikkmetoder).

    Returnerer:
        dict: Resultater med statistiske mål per kolonne.
    """
    df = pd.read_json(datafil, orient="records", lines=True)

    resultater = {}
    for kol in ["min", "mean", "max"]:
        verdier = df[kol].dropna().to_numpy()  # Konverter til NumPy-array
        resultater[kol] = {
            "gjennomsnitt": np.mean(verdier),
            "median": np.median(verdier),
            "standardavvik": np.std(verdier, ddof=1) 
        }

    return resultater



def beskriv_statistikk(datafil: str = "../../data/Havnivådata/havnivaadata.json") -> pd.DataFrame:
    """
    Bruker Pandas .describe() for å gi en statistisk oppsummering
    av kolonnene 'min', 'max' og 'mean' i havnivådatasettet.

    Returnerer:
        pd.DataFrame: Tabell med beskrivende statistikk.
    """
    df = pd.read_json(datafil, orient="records", lines=True)
    return df[["min", "mean", "max"]].describe()


def finn_mistenkelige_hopp(
    datafil: str = "../../data/Havnivådata/havnivaadata.json",
    kolonne: str = "mean",
    grense_faktor: float = 3.0
) -> pd.DataFrame:
    """
    Undersøker datasettet for unormale hopp i angitt "mean" kolonnen mellom måneder,
    som kan indikere trendforskyvning eller målefeil.

    Parametre:
        datafil (str): Relativ sti til JSON-datafil med havnivådata.
        kolonne (str): Kolonnen som skal analyseres (default = "mean").
        grense_faktor (float): Antall standardavvik som definerer et avvik (default = 3.0).

    Returnerer:
        pd.DataFrame: Rader hvor endringen mellom måneder overstiger grensen.
    """
    df = pd.read_json(datafil, orient="records", lines=True)
    df["iso_time"] = pd.to_datetime(df["iso_time"])
    df = df.sort_values("iso_time").reset_index(drop=True)
    df["måned_nr"] = range(len(df))

    # Beregn differanse mellom påfølgende verdier
    df[f"{kolonne}_diff"] = df[kolonne].diff()

    # Finn grense for unormale hopp
    grense = df[f"{kolonne}_diff"].std() * grense_faktor

    # Filtrer ut rader med mistenkelige hopp
    avvik = df[np.abs(df[f"{kolonne}_diff"]) > grense]

    return avvik[["iso_time", kolonne, f"{kolonne}_diff"]]

