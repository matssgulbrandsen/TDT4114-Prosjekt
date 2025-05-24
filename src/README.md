# 📂 src – Oversikt  
Strukturen er laget for å skille mellom hva funksjonene bruker av data beskriver albedo, havnivå og temperatur
De 3 mappene har i tilegg samme navn på undermapper for enkelhet og ryddig struktur.
src/
└── albedo_effekt_data/
│   └── dataanalyse.py        # Funksjoner som beregner statistiske mål og korrelasjon
│   └── databehandling.py       # Funksjoner som renser, formaterer og endrer DF
│   └── datainnsamling.py         # Funksjoner som henter inn data ved hjelp av API
│   └── dataprediksjon.py        # Funksjoner som utfører linær regresjon og predikerer fremtidig data
│   └── dataviualisering.py            # Funksjoner som lager visualiseringer og interaktive grafer
└──  Havnivådata/
│   └── dataanalyse.py        # -||-
│   └── databehandling.py       # -||-
│   └── datainnsamling         # -||-
│   └── dataprediksjon.py           # -||-
│   └── dataviualisering.py            # -||-
└──  tempraturdata/
|   └── dataanalyse.py        # -||-
|   └── databehandling.py       # -||-
|   └── datainnsamling         # -||-
|   └── dataprediksjon.py           # -||-
|   └── dataviualisering.py            # -||-
└── Sammenligning_av_miljodata/
    └── Sammenligning_miljodata.py   # Funksjon som sammenligner ulik miljødata i graf