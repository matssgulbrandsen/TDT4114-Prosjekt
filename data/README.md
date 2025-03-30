Denne mappen inneholder data som brukes til Albedo-oppgavene. Mappen har to hovedmapper: csv_albedo_effekt og albedo_effekt.

1. csv_albedo_effekt
Denne mappen inneholder CSV-filer med bearbeidet data knyttet til albedo-effekten. Dataene er hentet fra albedo_effekt-mappen og er filtrert for spesifikke variabler.

Innhold:
Filene er navngitt Albedo effekt (år).csv, der år er året for dataene.

CSV-filene inneholder kolonner som:

lat og lon: Breddegrad og lengdegrad.

AL-BB-DH, AL-BB-DH-ERR: Verdier relatert til albedo-effekten.

quality_flag: Kvalitetsvurdering av dataene.

2. albedo_effekt
Denne mappen inneholder NetCDF-filer med rådata for albedo-effekten.

Innhold:
Filene er navngitt NETCDF4_LSASAF_MSG_ALBEDO-D10v2_MSG-Disk_(år)06250000.nc, der (år) er året for dataene.

Disse filene inneholder råmålinger som blir bearbeidet til CSV-format i csv_albedo_effekt.