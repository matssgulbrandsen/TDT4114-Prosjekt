import pandas as pd
import numpy as np

def rens_manglende_verdier(
    df: pd.DataFrame,
    kolonner: list = None,
    metode: str = "mean"
) -> pd.DataFrame:
    """
    Identifiserer og håndterer manglende verdier (NaN) i en DataFrame med ulike strategier.

            - 'mean': Fyller inn manglende verdier med kolonnens gjennomsnitt.
            - 'median': Fyller inn manglende verdier med kolonnens median.
            - 'interpolate': Bruker lineær interpolasjon for å fylle inn mellomverdier (anbefalt for tidsserier).
            - 'ffill': Fyller inn manglende verdier med forrige tilgjengelige verdi ("forward fill").
            - 'bfill': Fyller inn manglende verdier med neste tilgjengelige verdi ("backward fill").
            - 'drop': Fjerner rader med manglende verdier i de valgte kolonnene.

    Returnerer:
        pd.DataFrame: En kopi av DataFrame der manglende verdier er håndtert etter valgt metode.

    Kommentar:
        For tidsseriedata gir 'interpolate' eller 'ffill'/'bfill' ofte mer realistisk resultat enn globalt gjennomsnitt,
        særlig hvis dataene har trend, sesong eller utvikling over tid.
    """
    if kolonner is None:
        kolonner = df.select_dtypes(include="number").columns.tolist()
    print("Antall manglende verdier per kolonne:\n", df[kolonner].isnull().sum())

    if metode == "mean":
        df[kolonner] = df[kolonner].fillna(df[kolonner].mean())
        print("Manglende verdier er fylt inn med kolonnens gjennomsnitt.")
    elif metode == "median":
        df[kolonner] = df[kolonner].fillna(df[kolonner].median())
        print("Manglende verdier er fylt inn med kolonnens median.")
    elif metode == "interpolate":
        df[kolonner] = df[kolonner].interpolate()
        print("Manglende verdier er fylt inn med lineær interpolasjon.")
    elif metode == "ffill":
        df[kolonner] = df[kolonner].fillna(method="ffill")
        print("Manglende verdier er fylt inn med forrige tilgjengelige verdi (ffill).")
    elif metode == "bfill":
        df[kolonner] = df[kolonner].fillna(method="bfill")
        print("Manglende verdier er fylt inn med neste tilgjengelige verdi (bfill).")
    elif metode == "drop":
        df = df.dropna(subset=kolonner)
        print("Rader med manglende verdier er fjernet.")
    else:
        raise ValueError(
            "Metode må være en av: 'mean', 'median', 'interpolate', 'ffill', 'bfill', 'drop'."
        )
    return df


def demonstrer_rensing_av_manglende_verdier(
    df,
    antall_nan_per_kolonne=3,
    metode="interpolate",
    random_state=42
):
    """
    Funksjon som:
      1) Legger til NaN i tilfeldige rader (og logger hvilke!),
      2) Skriver ut disse radene før rensing,
      3) Renser datasettet med bruk av rens_manglende_verdier,
      4) Skriver ut de samme radene etter rensing, hvis de finnes.
    """
    from Databehandling import rens_manglende_verdier

    rader_med_nan = set()
    df_copy = df.copy()
    kolonner = df.select_dtypes(include="number").columns.tolist()
    np.random.seed(random_state)
    for col in kolonner:
        idx = np.random.choice(df_copy.index, size=antall_nan_per_kolonne, replace=False)
        df_copy.loc[idx, col] = np.nan
        print(f"La til NaN i kolonne '{col}' på rader: {idx.tolist()}")
        rader_med_nan.update(idx.tolist())

    print("\nAntall manglende verdier etter tilsetning:")
    print(df_copy.isnull().sum())

    # Vis radene som fikk NaN, før rensing:
    print("\n--- Rader med NaN FØR rensing ---")
    print(df_copy.loc[sorted(rader_med_nan)])

    # Rens
    df_renset = rens_manglende_verdier(df_copy, metode=metode)

    print("\nAntall manglende verdier etter rensing:")
    print(df_renset.isnull().sum())

    print("\n--- Samme rader ETTER rensing ---")
    if metode == "drop":
        # Sjekk hvilke rader som faktisk finnes igjen. Måtte legges til fordi vi kan printe noe som ikke finnes lengere (drop).
        beholdt = [i for i in sorted(rader_med_nan) if i in df_renset.index]
        fjernet = [i for i in sorted(rader_med_nan) if i not in df_renset.index]
        if beholdt:
            print(df_renset.loc[beholdt])
        if fjernet:
            print(f"Rader fjernet av 'drop' (de hadde NaN): {fjernet}")
    else:
        print(df_renset.loc[sorted(rader_med_nan)])

    return df_renset



def sett_usannsynlige_til_nan(df: pd.DataFrame, kolonnegrenser: dict) -> pd.DataFrame:
    """
    Setter usannsynlige verdier (utenfor [min, max]) i gitte kolonner til NaN,
    men lar resten av raden være intakt.

    Returnerer:
        pd.DataFrame: Ny DataFrame hvor usannsynlige verdier satt til NaN.
    """
    df_renset = df.copy()
    for kol, (min_val, max_val) in kolonnegrenser.items():
        mask = (df_renset[kol] < min_val) | (df_renset[kol] > max_val)
        antall = mask.sum()
        df_renset.loc[mask, kol] = np.nan
        print(f"  Satt {antall} usannsynlige verdier til NaN i '{kol}' (utenfor [{min_val}, {max_val}])")
    return df_renset











