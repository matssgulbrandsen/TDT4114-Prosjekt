

## Havnivådata

## "metadata_datasetliste.json"

Denne fila inneholder en oversikt over alle tilgjengelige datasett som NASA Sealevel Nexus tilbyr. Den er hentet via API-endepunktet `/list` og lagres som JSON Lines med én linje per datasett.

| Kolonnenavn | Forklaring 
|-------------|------------
| `title`     | Navnet på datasettet (f.eks. "NASA_SSH_REF_SIMPLE_GRID_V1_Monthly") 
| `tileCount` | Antall tilgjengelige datapunkter 
| `iso_start` | Startdato for datasettet  
| `iso_end`   | Sluttdato for datasettet 

Filtrerte ikke ut noen kolonner siden alle var relevante

Datasettet brukes til å:
- Finne relevante datasett med god datamengde (`tileCount >= terskel`)
- Filtrere på tittel som inneholder "SSH"
- Analysere hvilke tidsperioder ulike datasett dekker

Vi bruker dette metadatafiltre som et pre-prosesseringsverktøy for å velge ut det mest relevante datasettet for videre analyse: `NASA_SSH_REF_SIMPLE_GRID_V1_Monthly` ble valgt og lagret under data/havnivaadata som "havnivaadata.json".

## "havnivaadata.json"

- **Filnavn**: `havnivaadata.json`
- **Format**: JSON Lines (en rad per linje)
- **Kilde**: Datasettet "NASA_SSH_REF_SIMPLE_GRID_V1_Monthly" fra sealevel-nexus.jpl.nasa.gov

### Originale kolonner 
| Kolonnenavn | Datatype | Forklaring | Brukes i analyse? 
|-------------|----------|------------|-------------------
| `min`       | float    | Minimum havnivå i måneden (meter)   ✅ 
| `mean`      | float    | Gjennomsnittlig havnivå (meter)     ✅ 
| `max`       | float    | Maksimalt havnivå i måneden (meter) ✅ 
| `std`       | float    | Standardavvik i målingene           ❌ 
| `cnt`       | int      | Antall målinger i perioden          ❌ 
| `time`      | int      | Unix-tid                            ❌ 
| `iso_time`  | datetime | Dato i ISO-format                   ✅ 

### Kolonner som ble fjernet
- `std` og `cnt` ble ikke fjernet. Ønsket å regne ut std selv og cnt var konstant over hele perioden så fjernet denne kolonnen.
- `time` (Unix) ble erstattet av `iso_time` for enklere datobehandling og lesbarhet.