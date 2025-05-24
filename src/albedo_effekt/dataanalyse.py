import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

def beregn_albedo_statistikk(
    referanse_fil="../data/albedo_effekt_data/csv_albedo_effekt/data_m-lavfeilmargin.csv",
    datafiler_pattern="../data/albedo_effekt_data/csv_albedo_effekt_komplett/Albedo *_komplett.csv",
    print_matrise=True
):
    """
    Leser referansefil og albedo-filer, beregner gjennomsnitt, median og standardavvik for hver fil/år.
    Returnerer matrise [år, gjennomsnitt, median, std] og lister for hver statistikk.
    """
    # Laster inn referanse datafil med lat/lon
    referanse_df = pd.read_csv(referanse_fil)

    # Henter CSV-filene
    datafiler = sorted(glob.glob(datafiler_pattern)) # Filene sorteres etter årstall

    # Tomme lister
    årstall_liste = []
    gjennomsnitt_liste = []
    median_liste = []
    standardavvik_liste = []

    # Gå gjennom hver fil og beregn statistikk
    for fil in datafiler:
        df = pd.read_csv(fil)
        felles = pd.merge(referanse_df, df, on=["lat", "lon"], how="inner")

        if "AL-BB-DH" in felles.columns and not felles["AL-BB-DH"].empty:
            gjennomsnitt = felles["AL-BB-DH"].mean()
            median = felles["AL-BB-DH"].median()
            std_avvik = felles["AL-BB-DH"].std()
        else:
            gjennomsnitt = median = std_avvik = float('nan')

        filnavn = os.path.basename(fil)
        årstall_str = ''.join(filter(str.isdigit, filnavn))
        if årstall_str:
            årstall = int(årstall_str)
        else:
            årstall = 0

        årstall_liste.append(årstall)
        gjennomsnitt_liste.append(float(gjennomsnitt))
        median_liste.append(float(median))
        standardavvik_liste.append(float(std_avvik))

    # Lager matrise: hver rad er [år, gjennomsnitt, median, standardavvik]
    albedo_matrise = np.column_stack((årstall_liste, gjennomsnitt_liste, median_liste, standardavvik_liste))

    # Printer matrise om ønskelig
    if print_matrise:
        np.set_printoptions(suppress=True, precision=4)
        print("\n📊 Albedo-statistikk matrise:")
        print("[År, Gjennomsnitt, Median, Standardavvik]")
        print(albedo_matrise)

    # Returnerer resultater for videre bruk
    return albedo_matrise, årstall_liste, gjennomsnitt_liste, median_liste, standardavvik_liste

def plot_albedo_heatmap_med_feilmargin(
    hovedfil="../data/albedo_effekt_data/csv_albedo_effekt/Albedo effekt 2004.csv",
    feilmarginfil="../data/albedo_effekt_data/csv_albedo_effekt/data_m-lavfeilmargin.csv",
    figsize=(10, 6),
    show_plot=True
):
    """
    Plotter et heatmap av albedo for et gitt år med punkter for lav feilmargin.
    Parametre:
        hovedfil:   Sti til hoveddatafil med albedo for et år.
        feilmarginfil: Sti til fil med lav feilmargin.
        figsize:    Tuple for figurstørrelse.
        show_plot:  Om plt.show() skal kjøres automatisk.
    Returnerer:
        fig, ax
    """
    # Les inn data
    df_main  = pd.read_csv(hovedfil)
    df_error = pd.read_csv(feilmarginfil)

    # Unike, sorterte koordinater
    lat_vals = np.sort(df_main["lat"].unique())
    lon_vals = np.sort(df_main["lon"].unique())

    # 2D grid for albedo
    albedo_grid = (
        df_main
        .pivot(index="lat", columns="lon", values="AL-BB-DH")
        .reindex(index=lat_vals, columns=lon_vals)
    )

    # Koordinatgrenser
    lon_min, lon_max = lon_vals.min(), lon_vals.max()
    lat_min, lat_max = lat_vals.min(), lat_vals.max()

    # Plot
    fig, ax = plt.subplots(figsize=figsize)

    # Heatmap
    im = ax.imshow(
        albedo_grid,
        cmap="viridis",
        extent=[lon_min, lon_max, lat_min, lat_max],
        origin="lower",
        aspect="auto"
    )
    plt.colorbar(im, ax=ax, label="Albedo (AL-BB-DH)")

    # Scatter for lav feilmargin
    ax.scatter(
        df_error["lon"],
        df_error["lat"],
        color='Red',
        s=10,
        label="Lav feilmargin",
        alpha=0.7
    )

    ax.set_title("Albedo med områder med lav feilmargin")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    plt.tight_layout()
    if show_plot:
        plt.show()

    return fig, ax

def statistikk_albedo(
    data_dir="../data/albedo_effekt_data/csv_albedo_effekt",
    datafiler_pattern="Albedo*.csv",
    albedo_min=0.3,
    print_matrise=True
):
    """
    Regner ut gjennomsnitt, median, std for AL-BB-DH > 0.3 for hvert år separat.
    Henter alle punkter med albedo over 0.3 uavhengig av tidligere år.
    
    Returnerer:
        albedo_matrise, årstall, gjennomsnitt, median, std
    """

    datafiler = sorted(glob.glob(os.path.join(data_dir, datafiler_pattern)))
    årstall_liste = []
    gjennomsnitt_liste = []
    median_liste = []
    std_liste = []

    for fil in datafiler:
        df = pd.read_csv(fil)
        # Kun punkter over grensen dette året!
        utvalg = df[df["AL-BB-DH"] > albedo_min]
        if not utvalg.empty:
            gjennomsnitt = utvalg["AL-BB-DH"].mean()
            median = utvalg["AL-BB-DH"].median()
            std = utvalg["AL-BB-DH"].std()
        else:
            gjennomsnitt = median = std = np.nan

        årstall = int(''.join(filter(str.isdigit, os.path.basename(fil))))
        årstall_liste.append(årstall)
        gjennomsnitt_liste.append(gjennomsnitt)
        median_liste.append(median)
        std_liste.append(std)

    # Sorter etter år
    sortert_indeks = np.argsort(årstall_liste)
    årstall = np.array(årstall_liste)[sortert_indeks]
    gjennomsnitt = np.array(gjennomsnitt_liste)[sortert_indeks]
    median = np.array(median_liste)[sortert_indeks]
    std = np.array(std_liste)[sortert_indeks]
    albedo_matrise = np.column_stack((årstall, gjennomsnitt, median, std))

    if print_matrise:
        print("\n📊 Statistikkmatrise (bare punkter > 0.3, for hvert år separat):")
        print("[År, Gjennomsnitt, Median, Standardavvik]")
        np.set_printoptions(suppress=True, precision=4)
        print(albedo_matrise)

    return albedo_matrise, årstall, gjennomsnitt, median, std

def albedo_statistikk_faste_2004_punkter(
    referansefil="../data/albedo_effekt_data/csv_albedo_effekt/Albedo effekt 2004.csv",
    feilmarginfil="../data/albedo_effekt_data/csv_albedo_effekt/data_m-lavfeilmargin.csv",
    datafiler_pattern="../data/albedo_effekt_data/csv_albedo_effekt/Albedo*.csv",
    albedo_grense=0.3,
    print_matrise=True
):
    """
    Beregn og plott albedo-statistikk for hvert år,
    men kun for punkter som i 2004 hadde høy albedo (> albedo_grense) og lav feilmargin.
    
    Returnerer:
        albedo_matrise, årstall, gjennomsnitt, median, std
    """
    # Les inn referanse- og feilmarginfiler
    referanse_2004 = pd.read_csv(referansefil)
    feilmargin = pd.read_csv(feilmarginfil)

    # Felles punkter med lav feilmargin og høy albedo i 2004
    felles_2004 = pd.merge(referanse_2004, feilmargin, on=["lat", "lon"], how="inner")
    referanse_punkter = felles_2004[(felles_2004["AL-BB-DH"] > albedo_grense)][["lat", "lon"]]
    print(f"🔍 Antall referansepunkter: {len(referanse_punkter)}")

    # Hent alle albedo-års-filer
    datafiler = sorted(glob.glob(datafiler_pattern))

    # Lister for lagring
    årstall_liste = []
    gjennomsnitt_liste = []
    median_liste = []
    std_liste = []

    # Gå gjennom hvert år, bruk kun de faste punktene fra 2004
    for fil in datafiler:
        df = pd.read_csv(fil)
        felles = pd.merge(referanse_punkter, df, on=["lat", "lon"], how="inner")
        if not felles.empty and "AL-BB-DH" in felles.columns:
            gjennomsnitt = felles["AL-BB-DH"].mean()
            median = felles["AL-BB-DH"].median()
            std = felles["AL-BB-DH"].std()
        else:
            gjennomsnitt = median = std = np.nan

        årstall = int(''.join(filter(str.isdigit, os.path.basename(fil))))
        årstall_liste.append(årstall)
        gjennomsnitt_liste.append(gjennomsnitt)
        median_liste.append(median)
        std_liste.append(std)

    # Sorter etter år
    sortert_indeks = np.argsort(årstall_liste)
    årstall = np.array(årstall_liste)[sortert_indeks]
    gjennomsnitt = np.array(gjennomsnitt_liste)[sortert_indeks]
    median = np.array(median_liste)[sortert_indeks]
    std = np.array(std_liste)[sortert_indeks]

    albedo_matrise = np.column_stack((årstall, gjennomsnitt, median, std))
    if print_matrise:
        print(f"Gjennomsnittlig forskjell mellom median og gjennomsnitt {np.mean(np.abs(albedo_matrise[:,1] - albedo_matrise[:,2])):.4f}")
        print("\n📊 Statistikkmatrise for faste snøpunkter:")
        print("[År, Gjennomsnitt, Median, Standardavvik]")
        np.set_printoptions(suppress=True, precision=4)
        print(albedo_matrise)

    return albedo_matrise, årstall, gjennomsnitt, median, std

def pearson_albedo_vs_year(albedo_matrise):
    """
    Beregner Pearson-korrelasjon mellom år og albedo-gjennomsnitt.
    """
    x = np.array(albedo_matrise[:, 0])
    y = np.array(albedo_matrise[:, 1])
    mask = ~np.isnan(y)
    x = x[mask]
    y = y[mask]
    r, p = pearsonr(x, y)
    print(f"Pearson korrelasjon mellom år og albedo: r = {r:.4f}, p-verdi = {p:.4f}")
    return r, p

def beskriv_albedo_statistikk(df, kolonne="AL-BB-DH"):
    """
    Skriver ut og returnerer statistisk sammendrag for en kolonne AL-BB-DH.
    """
    beskrivelse = df[kolonne].describe()
    print(f"Statistikk for {kolonne}:")
    print(beskrivelse)
    return beskrivelse
