# 📂 data – Oversikt  
Prosjektet benytter flere typer observasjonsdata som er delt inn i egne under­mapper.  
Strukturen er laget for å skille mellom hva dataene beskriver albedo, havnivå og temperatur

data/
└── albedo_effekt_data/
│    └── csv_albedo_effekt.csv           # Netcdf filer omgjort til CSV og hentet ut viktigste data
│    └── csv_albedo_effekt_komplett.csv   # Sjekket og renset CSV-filer
│    └── netcdf.nc                     # NETCDF4 - Orginal filer
└── havnivå_data/ 
|   └── havnivaadata.json        # månedlige målinger av havnivå fra 1992 til 2025. (.json format)
|                                # Følgende nøkkelverdier: iso time, mean, min, max     
│   └── metadata_datasetliste.json  #  Denne fila inneholder en oversikt over alle. (.json format)
|                                    # tilgjengelige datasett som NASA Sealevel Nexus tilbyr.
└── tempraturdata/                   
    └── temperaturdata.csv    # målinger av temperatur en gang i timen 1950-2025
    └── temperaturdata_feilverdier.csv    # kopi av temperaturdata.csv med manuel manipulering
                                            # av verdier omgjort til Nans eller urealistiske