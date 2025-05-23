import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display
from sklearn.linear_model import LinearRegression

class Visualisering:

    def plot_albedo_med_std(
        self,
        årstall_liste, 
        gjennomsnitt_liste,
        median_liste,
        standardavvik_liste,
        figur_størrelse=(12, 6),
        vis_plot=True,
        tittel="Albedo-statistikk per år",
        ylabel="Albedo"
    ):
        """
        Plotter gjennomsnitt, median og standardavvik per år på én akse.
        Standardavvik vises som et fylt område rundt gjennomsnittet.
        """
        år = np.array(årstall_liste)
        gj = np.array(gjennomsnitt_liste)
        median = np.array(median_liste)
        std = np.array(standardavvik_liste)

        fig, ax = plt.subplots(figsize=figur_størrelse)

        # Plot gjennomsnitt og median
        ax.plot(år, gj, 'o-', label='Gjennomsnitt', color='blue')
        ax.plot(år, median, 's--', label='Median', color='green')

        # Standardavvik som skyggeområde
        ax.fill_between(år, gj - std, gj + std,
                        color='blue', alpha=0.1, label='Standardavvik')

        ax.set_title(tittel, pad=20)
        ax.set_xlabel("År", fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper right')
        plt.tight_layout()

        if vis_plot:
            plt.show()

        return fig, ax

    def plot_albedo_heatmap_med_feilmargin(
        self,
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

        # Prikker for lav feilmargin
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

    def statistikk_faste_referansepunkter_visualisering(
        self,
        årstall,
        gjennomsnitt,
        median,
        std
    ):
        referanse_år=2004
        albedo_min=0.3
        
        plt.figure(figsize=(12, 6))
        plt.plot(årstall, gjennomsnitt, 'o-', label='Gjennomsnitt', color='blue')
        plt.plot(årstall, median, 's--', label='Median', color='green')
        plt.fill_between(årstall, gjennomsnitt - std, gjennomsnitt + std, color='blue', alpha=0.1, label='Standardavvik')
        plt.title("Albedo-statistikk for faste snøpunkter ({}-referanse)\nFiltrert: Albedo > {} og Lav feilmargin".format(referanse_år, albedo_min), pad=20)
        plt.xlabel("År", fontsize=12)
        plt.ylabel("Albedo", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()

    def albedo_statistikk_faste_2004_punkter_visualisering(
        self,
        årstall,
        gjennomsnitt,
        median,
        std
    ):
        referanse_år=2004
        albedo_min=0.3
        
        """
        Beregn og plott albedo-statistikk for hvert år,
        men kun for punkter som i 2004 som hadde høy albedo (> albedo_grense) og lav feilmargin.
        
        Returnerer:
            årstall, gjennomsnitt, median, std
        """
       
        plt.figure(figsize=(12, 6))
        plt.plot(årstall, gjennomsnitt, 'o-', label='Gjennomsnitt', color='blue')
        plt.plot(årstall, median, 's--', label='Median', color='green')
        plt.fill_between(årstall, gjennomsnitt - std, gjennomsnitt + std, color='blue', alpha=0.1, label='Standardavvik')
        plt.title(f"Albedo-statistikk for faste snøpunkter ({referanse_år}-referanse)\nFiltrert: Albedo > {albedo_min} og Lav feilmargin", pad=20)
        plt.xlabel("År", fontsize=12)
        plt.ylabel("Albedo", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()

        return

    def hent_stats_dataframe(
        self,
        referansefil="../data/albedo_effekt_data/csv_albedo_effekt/Albedo effekt 2004.csv",
        feilmarginfil="../data/albedo_effekt_data/csv_albedo_effekt/data_m-lavfeilmargin.csv",
        albedo_min=0.3,
        albedo_data_pattern="../data/albedo_effekt_data/csv_albedo_effekt/Albedo*.csv"
    ):
        """
        Returnerer DataFrame med [År, Gjennomsnittlig albedo] for kun faste snøpunkter fra 2004 med høy albedo og lav feilmargin.
        """
        referanse_2004 = pd.read_csv(referansefil)
        feilmargin = pd.read_csv(feilmarginfil)
        felles_2004 = pd.merge(referanse_2004, feilmargin, on=["lat","lon"], how="inner")
        ref_punkter = felles_2004[felles_2004["AL-BB-DH"] > albedo_min][["lat","lon"]]
        årstall, gjennomsnitt = [], []
        for fil in sorted(glob.glob(albedo_data_pattern)):
            df = pd.read_csv(fil)
            df["lat"] = df["lat"].round(6); df["lon"] = df["lon"].round(6)
            felles = pd.merge(ref_punkter, df, on=["lat","lon"], how="inner")
            årstall.append(int(''.join(filter(str.isdigit, os.path.basename(fil)))))
            gjennomsnitt.append(felles["AL-BB-DH"].mean() if "AL-BB-DH" in felles else np.nan)
        stats = pd.DataFrame({"År": årstall, "Gjennomsnittlig albedo": gjennomsnitt})
        return stats

    def plot_interactive_albedo(
        self,
        stats: pd.DataFrame,
        year_min=None,
        year_max=None,
        show_trend=True
    ):
        """
        Plotter interaktivt (med widgets) utviklingen i gjennomsnittlig albedo.
        Kan brukes direkte fra notebook.
        """
        if year_min is None:
            year_min = stats["År"].min()
        if year_max is None:
            year_max = stats["År"].max()

        def plot_func(year_range, show_trend):
            min_year, max_year = year_range
            df = stats[(stats["År"] >= min_year) & (stats["År"] <= max_year)]
            plt.figure(figsize=(10, 5))
            sns.lineplot(data=df, x="År", y="Gjennomsnittlig albedo", marker="o", label="Årlig gj.snitt")
            if show_trend and len(df) > 1:
                sns.regplot(data=df, x="År", y="Gjennomsnittlig albedo", scatter=False,
                            label="Trendlinje", ci=None, line_kws={"linestyle":"--"})
                koeff = np.polyfit(df["År"], df["Gjennomsnittlig albedo"], 1)
                stigning = koeff[0]
                snitt_albedo = df["Gjennomsnittlig albedo"].mean()
                prosent_endring = (stigning / snitt_albedo) * 100
                retning = "økning" if prosent_endring > 0 else "nedgang"
                print(f"📉 Trend: {prosent_endring:.2f}% {retning} i albedo per år ({stigning:.5f} absolutt endring)")

            plt.title(f"Albedo-utvikling {min_year}–{max_year}")
            plt.xlabel("År"); plt.ylabel("Albedo")
            plt.grid(True, linestyle="--", alpha=0.5)
            plt.legend()
            plt.show()

        year_slider = widgets.IntRangeSlider(
            value=[year_min, year_max],
            min=year_min, max=year_max,
            step=1, description="År-range:"
        )
        trend_toggle = widgets.Checkbox(value=True, description="Vis trendlinje")

        interactive_plot = widgets.interactive(plot_func,
                                               year_range=year_slider,
                                               show_trend=trend_toggle)
        display(interactive_plot)

    def plot_interaktiv_heatmap_albedo(
        self,
        data_pattern="../data/albedo_effekt_data/csv_albedo_effekt_komplett/Albedo*_komplett.csv",
        figsize=(9, 5)
    ):
        """
        Interaktivt heatmap for albedo per år, basert på CSV-filer for hvert år.
        Viser kun albedo (AL-BB-DH) – ingen filtrering på lav feilmargin.

        Parametre:
            data_pattern: glob pattern for å finne albedo-filer, én per år.
            figsize: figurstørrelse for plot.

        Bruk: plot_interaktiv_heatmap_albedo()
        """
        # Hent alle relevante csv-filer
        filelist = sorted(glob.glob(data_pattern))
        if not filelist:
            print("Ingen albedo-filer funnet med mønster:", data_pattern)
            return

        # Ekstraher tilgjengelige år fra filnavnene
        year_list = [int(''.join(filter(str.isdigit, os.path.basename(f)))) for f in filelist]
        year_file_map = dict(zip(year_list, filelist))

        år_slider = widgets.SelectionSlider(
            options=year_list,
            value=year_list[0],
            description='Velg år:',
            continuous_update=False,
            style={"description_width": "initial"},
            layout=widgets.Layout(width="70%")
        )

        output = widgets.Output()

        def plot_heatmap(selected_year):
            output.clear_output()
            with output:
                f = year_file_map[selected_year]
                df = pd.read_csv(f)
                lat_vals = np.sort(df["lat"].unique())
                lon_vals = np.sort(df["lon"].unique())
                albedo_grid = (
                    df.pivot(index="lat", columns="lon", values="AL-BB-DH")
                      .reindex(index=lat_vals, columns=lon_vals)
                )
                fig, ax = plt.subplots(figsize=figsize)
                im = ax.imshow(
                    albedo_grid,
                    cmap="viridis",
                    extent=[lon_vals.min(), lon_vals.max(), lat_vals.min(), lat_vals.max()],
                    origin="lower",
                    aspect="auto"
                )
                plt.colorbar(im, ax=ax, label="Albedo (AL-BB-DH)")
                ax.set_title(f"Albedo Heatmap {selected_year}")
                ax.set_xlabel("Longitude")
                ax.set_ylabel("Latitude")
                plt.tight_layout()
                plt.show()

        widgets.interactive_output(plot_heatmap, {"selected_year": år_slider})
        display(widgets.VBox([år_slider, output]))

    def vis_albedo_meny(self):
        """
        Interaktiv meny for å velge og vise ulike albedo-visualiseringer.
        Brukes rett fra notebook: vis_albedo_meny()
        """
        output = widgets.Output()
        menyvalg = widgets.Dropdown(
            options=[
                ("📊 Linjeplot: Årlig gj.snitt, median, std", "plot_albedo_med_std"),
                ("🔥 Heatmap: Albedo + lav feilmargin", "plot_albedo_heatmap_med_feilmargin"),
                ("📈 Faste referansepunkter (statistikk)", "statistikk_faste_referansepunkter"),
                ("🟦 Faste punkter fra 2004 med høy albedo", "albedo_statistikk_faste_2004"),
                ("🌟 Interaktiv: Gj.snittlig albedo", "plot_interactive_albedo")
            ],
            description="Velg graf:",
            style={"description_width": "initial"},
            layout=widgets.Layout(width="70%")
        )
        knapp = widgets.Button(description="Vis valgt graf", button_style="success")

        # Følgende funksjoner må finnes/importeres i ditt miljø!
        from .dataanalyse import (
            beregn_albedo_statistikk,
            statistikk_albedo,
            albedo_statistikk_faste_2004_punkter,
        )

        def vis_plot(_):
            output.clear_output()
            with output:
                valg = menyvalg.value
                if valg == "plot_albedo_med_std":
                    albedo_matrise, årstall_liste, gjennomsnitt_liste, median_liste, std_liste = beregn_albedo_statistikk()
                    self.plot_albedo_med_std(årstall_liste, gjennomsnitt_liste, median_liste, std_liste)
                elif valg == "plot_albedo_heatmap_med_feilmargin":
                    self.plot_albedo_heatmap_med_feilmargin(
                        hovedfil="../data/albedo_effekt_data/csv_albedo_effekt/Albedo effekt 2004.csv",
                        feilmarginfil="../data/albedo_effekt_data/csv_albedo_effekt/data_m-lavfeilmargin.csv"
                    )
                elif valg == "statistikk_faste_referansepunkter":
                    albedo_matrise, årstall, gjennomsnitt, median, std = statistikk_albedo()
                    self.statistikk_faste_referansepunkter_visualisering(årstall, gjennomsnitt, median, std)
                elif valg == "albedo_statistikk_faste_2004":
                    albedo_matrise, årstall, gjennomsnitt, median, std = albedo_statistikk_faste_2004_punkter()
                    self.albedo_statistikk_faste_2004_punkter_visualisering(årstall, gjennomsnitt, median, std)
                elif valg == "plot_interactive_albedo":
                    stats = self.hent_stats_dataframe()
                    self.plot_interactive_albedo(stats)
                else:
                    print("Ingen graf valgt.")

        knapp.on_click(vis_plot)
        vbox = widgets.VBox([menyvalg, knapp, output])
        display(vbox)

    def plot_manglende_verdier_effekt(
        self,
        stats
    ):
        """
        Visualiserer hvordan interpolasjon av manglende verdier (2013 og 2022)
        påvirker trendlinje og prediksjon. Kun de interpolerte verdiene markeres separat.
        """
        # Trendlinje med alle verdier (ekte)
        X_full = stats[["År"]]
        y_full = stats["Gjennomsnittlig albedo"]
        model_full = LinearRegression()
        model_full.fit(X_full, y_full)
        trend_full = model_full.predict(X_full)
        
        # Kopi med 2013 og 2022 som manglende
        stats_missing = stats.copy()
        stats_missing.loc[stats_missing["År"].isin([2013, 2022]), "Gjennomsnittlig albedo"] = np.nan
        # Interpolér bare de to årene
        stats_interp = stats_missing.copy()
        stats_interp["Gjennomsnittlig albedo"] = stats_interp["Gjennomsnittlig albedo"].interpolate(method="linear")
        
        # Trendlinje med interpolert datasett
        X_interp = stats_interp[["År"]]
        y_interp = stats_interp["Gjennomsnittlig albedo"]
        model_interp = LinearRegression()
        model_interp.fit(X_interp, y_interp)
        trend_interp = model_interp.predict(X_interp)

        # Ploter ekte datapunkter
        plt.figure(figsize=(12, 6))
        # Plotter alle originale datapunkter (unntatt 2013 og 2022, som blir NaN her)
        mask_ekte = ~stats["År"].isin([2013, 2022])
        plt.scatter(stats.loc[mask_ekte, "År"], stats.loc[mask_ekte, "Gjennomsnittlig albedo"],
                    color="blue", label="Ekte data", s=70, zorder=2)
        # Plotter de to interpolerte punktene
        mask_interp = stats["År"].isin([2013, 2022])
        plt.scatter(stats_interp.loc[mask_interp, "År"], stats_interp.loc[mask_interp, "Gjennomsnittlig albedo"],
                    color="orange", label="Interpolert (2013/2022)", s=100, marker="s", zorder=3)
        # Trendlinjer
        plt.plot(stats["År"], trend_full, '-', color="blue", label="Trendlinje (ekte)", zorder=1)
        plt.plot(stats_interp["År"], trend_interp, '--', color="orange", label="Trendlinje (interpolert)", zorder=1)
        plt.title("Effekt av interpolasjon av manglende verdier (kun 2013 og 2022)")
        plt.xlabel("År")
        plt.ylabel("Gjennomsnittlig albedo")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()

        # Beregner stigning for begge trendlinjer
        stigning_full = model_full.coef_[0]
        stigning_interp = model_interp.coef_[0]
        diff = stigning_interp - stigning_full
        print(f"Stigning for trend (ekte): {stigning_full:.4f}")
        print(f"Stigning for trend (interpolert): {stigning_interp:.4f}")
        print(f"Forskjell i stigning på grunn av interpolasjon: {diff:.4f}")



