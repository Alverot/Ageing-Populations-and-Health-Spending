# Lab 2 – Results

Results of Tasks 2.2, 2.3 and 2.4. All numbers come from the database `global_health`
after the imports of 2026-11-13 (data downloaded the same day).

## Task 2.2 – IQR outlier flag

For each indicator, `clean_observations()` in `etl/clean.py` computes Q1, Q3 and
IQR = Q3 − Q1 over all its rows, and sets `is_outlier = true` for values below
Q1 − 1.5 × IQR or above Q3 + 1.5 × IQR. The rows are kept, only flagged. The column was
added by the Alembic migration `migrations/versions/0002_observation_is_outlier.py`.

```sql
SELECT i.code, COUNT(*) FILTER (WHERE o.is_outlier) AS flagged, COUNT(*) AS rows
FROM observation o JOIN indicator i USING (indicator_id)
GROUP BY i.code ORDER BY i.code;
```

| Indicator | Name | Rows | Flagged | Flagged % |
|---|---|---:|---:|---:|
| GHED_CHEGDP_SHA2011 | Current health expenditure (% of GDP) | 4,540 | 69 | 1.5% |
| GHED_CHE_pc_US_SHA2011 | Current health expenditure per capita (US$) | 4,537 | 632 | 13.9% |
| GHED_OOPSCHE_SHA2011 | Out-of-pocket expenditure (% of CHE) | 4,540 | 0 | 0.0% |
| life-expectancy | Life expectancy at birth (OWID) | 5,160 | 54 | 1.0% |
| NY.GDP.PCAP.CD | GDP per capita (US$) | 5,242 | 423 | 8.1% |
| SH.MED.BEDS.ZS | Hospital beds (per 1,000 people) | 2,945 | 78 | 2.6% |
| SP.POP.65UP.TO.ZS | Population ages 65 and above (%) | 5,425 | 25 | 0.5% |
| WHOSIS_000001 | Life expectancy at birth (WHO) | 13,320 | 66 | 0.5% |
| WHOSIS_000002 | Healthy life expectancy (HALE) | 13,320 | 107 | 0.8% |

**Explanation.**

- **Money indicators** (health spending per person, GDP per person) have the most flagged rows.
  Most countries have low values and a few rich countries have very high values, so the
  distribution has a long right tail. Everything above about 2,150 US$ of health spending per
  person or 50,900 US$ of GDP per person is flagged. These values are real, not errors, which
  is why they are only flagged.
- **Spending as % of GDP, hospital beds and population 65+** are flagged only at the top
  (above about 13.8% of GDP, 9.6 beds per 1,000 people and 26.9% aged 65+). The 25 flagged
  rows for population 65+ are only two countries: Monaco (2010–2024) and Japan (2015–2024),
  the oldest populations in the data.
- **Life expectancy and HALE** are flagged only at the bottom (below about 45.6 years for WHO
  life expectancy), for example the Central African Republic around 2009.
- **Out-of-pocket spending** has no outliers: its values are spread over the whole 0–88%
  range, so no value is far from the others.

## Task 2.3 – Running the imports twice

The three imports were run twice in a row:

```bash
python -m etl.import_worldbank
python -m etl.import_who
python -m etl.import_owid
```

Output of the first run (the second run is the same, with `inserted=0` and `updated` equal to
the first run's `inserted`):

```
countries                upserted=217
SP.POP.65UP.TO.ZS        raw=  6650 rejected=  1225 inserted=  5425 updated=     0
NY.GDP.PCAP.CD           raw=  6650 rejected=  1408 inserted=  5242 updated=     0
SH.MED.BEDS.ZS           raw=  6650 rejected=  3705 inserted=  2945 updated=     0
GHED_CHE_pc_US_SHA2011   raw=  4585 rejected=    48 inserted=  4537 updated=     0
GHED_CHEGDP_SHA2011      raw=  4588 rejected=    48 inserted=  4540 updated=     0
GHED_OOPSCHE_SHA2011     raw=  4588 rejected=    48 inserted=  4540 updated=     0
WHOSIS_000001            raw= 13320 rejected=     0 inserted= 13320 updated=     0
WHOSIS_000002            raw= 13320 rejected=     0 inserted= 13320 updated=     0
life-expectancy          raw= 21565 rejected= 16405 inserted=  5160 updated=     0
```

**Rows per indicator (overview query).** The counts are the same after the first and the
second run:

| Code | Name | Rows | First year | Last year |
|---|---|---:|---:|---:|
| GHED_CHEGDP_SHA2011 | Current health expenditure | 4,540 | 2000 | 2023 |
| GHED_CHE_pc_US_SHA2011 | Current health expenditure per capita | 4,537 | 2000 | 2023 |
| GHED_OOPSCHE_SHA2011 | Out-of-pocket expenditure | 4,540 | 2000 | 2023 |
| life-expectancy | Life expectancy at birth (long series) | 5,160 | 2000 | 2023 |
| NY.GDP.PCAP.CD | GDP per capita | 5,242 | 2000 | 2024 |
| SH.MED.BEDS.ZS | Hospital beds | 2,945 | 2000 | 2023 |
| SP.POP.65UP.TO.ZS | Population ages 65 and above | 5,425 | 2000 | 2024 |
| WHOSIS_000001 | Life expectancy at birth | 13,320 | 2000 | 2023 |
| WHOSIS_000002 | Healthy life expectancy (HALE) at birth | 13,320 | 2000 | 2023 |
| **Total** | | **59,029** | | |

**Duplicates (query 2):** no rows, after both runs.

**import_log.** One row per indicator and run (18 rows). Besides `rows_loaded`, the table has
`rows_inserted`, `rows_updated` and `rows_rejected` (migration
`0003_import_log_row_counts.py`), so it shows how many rows were imported and how many were
rejected by the cleaning rules:

| id | Source | Indicator | loaded | inserted | updated | rejected |
|---:|---|---|---:|---:|---:|---:|
| 1 | World Bank | SP.POP.65UP.TO.ZS | 5,425 | 5,425 | 0 | 1,225 |
| 2 | World Bank | NY.GDP.PCAP.CD | 5,242 | 5,242 | 0 | 1,408 |
| 3 | World Bank | SH.MED.BEDS.ZS | 2,945 | 2,945 | 0 | 3,705 |
| 4 | WHO | GHED_CHE_pc_US_SHA2011 | 4,537 | 4,537 | 0 | 48 |
| 5 | WHO | GHED_CHEGDP_SHA2011 | 4,540 | 4,540 | 0 | 48 |
| 6 | WHO | GHED_OOPSCHE_SHA2011 | 4,540 | 4,540 | 0 | 48 |
| 7 | WHO | WHOSIS_000001 | 13,320 | 13,320 | 0 | 0 |
| 8 | WHO | WHOSIS_000002 | 13,320 | 13,320 | 0 | 0 |
| 9 | OWID | life-expectancy | 5,160 | 5,160 | 0 | 16,405 |
| 10 | World Bank | SP.POP.65UP.TO.ZS | 5,425 | 0 | 5,425 | 1,225 |
| 11 | World Bank | NY.GDP.PCAP.CD | 5,242 | 0 | 5,242 | 1,408 |
| 12 | World Bank | SH.MED.BEDS.ZS | 2,945 | 0 | 2,945 | 3,705 |
| 13 | WHO | GHED_CHE_pc_US_SHA2011 | 4,537 | 0 | 4,537 | 48 |
| 14 | WHO | GHED_CHEGDP_SHA2011 | 4,540 | 0 | 4,540 | 48 |
| 15 | WHO | GHED_OOPSCHE_SHA2011 | 4,540 | 0 | 4,540 | 48 |
| 16 | WHO | WHOSIS_000001 | 13,320 | 0 | 13,320 | 0 |
| 17 | WHO | WHOSIS_000002 | 13,320 | 0 | 13,320 | 0 |
| 18 | OWID | life-expectancy | 5,160 | 0 | 5,160 | 16,405 |

(Source names shortened; in the table they are "World Bank Indicators API",
"WHO Global Health Observatory (GHO) OData API" and "Our World in Data".)

**Explanation.** In the second run every row already existed, so the upsert
(`INSERT ... ON CONFLICT ON CONSTRAINT uq_observation DO UPDATE`) updated it instead of
inserting a new one: 0 inserted, 59,029 updated, and the row counts did not change. The
import can therefore be re-run safely.

**Why rows are rejected.** Over one run 22,935 rows were rejected:

- World Bank: 1,225 rows per indicator are regions and income groups ("World",
  "Euro area", "High income", ...), not countries. Hospital beds and GDP also have empty values
  (2,480 and 183 rows). Empty values are never stored as 0.
- WHO health spending: 48 rows per indicator belong to the Cook Islands and Niue, which are
  not in the World Bank country list.
- OWID: 12,738 rows are years before 2000 and 3,667 rows are regions or continents without a
  country code.

## Task 2.4 – Data quality checks

**1. Countries: one row per economy, no aggregates**

| countries | regions |
|---:|---:|
| 217 | 7 |

The World Bank lists 296 economies; the 79 aggregates (region "Aggregates") are left out by
the transform, so 217 countries remain, spread over the 7 World Bank regions. No "World" or
"Euro area" rows.

**2. No duplicates on the natural key**

No rows. The unique constraint `uq_observation (country_iso3, indicator_id, year, sex)` makes
duplicates impossible, and the cleaning step also removes duplicates inside one download before
the insert.

**3. Values inside the plausible bounds**

| Code | Unit | Min | Max | Avg |
|---|---|---:|---:|---:|
| GHED_CHEGDP_SHA2011 | % of GDP | 1.2226 | 27.0897 | 6.23 |
| GHED_CHE_pc_US_SHA2011 | current US$ | 4.1758 | 13,473.1934 | 987.56 |
| GHED_OOPSCHE_SHA2011 | % of current health expenditure | 0.0446 | 87.9039 | 33.49 |
| life-expectancy | years | 14.6655 | 86.3724 | 70.78 |
| NY.GDP.PCAP.CD | current US$ | 109.5938 | 288,001.5749 | 16,314.53 |
| SH.MED.BEDS.ZS | per 1,000 people | 0.1500 | 22.2700 | 3.43 |
| SP.POP.65UP.TO.ZS | % of total population | 0.8625 | 37.3193 | 8.36 |
| WHOSIS_000001 | years | 24.4000 | 87.1000 | 70.54 |
| WHOSIS_000002 | years | 21.3000 | 74.8000 | 60.94 |

Every value is inside the bounds in `_INDICATOR_BOUNDS` (`etl/clean.py`): percentages between 0
and 100, life expectancy between 0 and 120 years, beds up to 50 per 1,000, money values above 0.
The extremes are real: the highest GDP per person is Monaco (2024), the highest health spending
per person is the United States (2023), the highest life expectancy is Japan (2020), and the
lowest life expectancy is the Central African Republic (2009). The very low OWID value for the
Central African Republic (14.7 years) is what OWID publishes; it is kept and flagged as an
outlier.

**4. Only known sex codes**

| sex | rows |
|---|---:|
| BTSX | 41,269 |
| FMLE | 8,880 |
| MLE | 8,880 |

Only the three codes of the `Sex` enum. WHO's `SEX_BTSX`, `SEX_MLE` and `SEX_FMLE` were
mapped to them, and sources without a sex split were stored as `BTSX`. Only WHO life expectancy
and HALE are split by sex (4,440 rows each for men and for women).

**5. No missing values and only years inside the window**

| null_values | out_of_window |
|---:|---:|
| 0 | 0 |

Empty values are dropped by the cleaning step and years outside 2000–2024 are removed.

**6. Rows stored match the last import of each indicator**

| Indicator | rows_loaded | rows_stored |
|---|---:|---:|
| GHED_CHEGDP_SHA2011 | 4,540 | 4,540 |
| GHED_CHE_pc_US_SHA2011 | 4,537 | 4,537 |
| GHED_OOPSCHE_SHA2011 | 4,540 | 4,540 |
| life-expectancy | 5,160 | 5,160 |
| NY.GDP.PCAP.CD | 5,242 | 5,242 |
| SH.MED.BEDS.ZS | 2,945 | 2,945 |
| SP.POP.65UP.TO.ZS | 5,425 | 5,425 |
| WHOSIS_000001 | 13,320 | 13,320 |
| WHOSIS_000002 | 13,320 | 13,320 |

All equal. Both imports read the same downloaded files, so the second run loaded exactly the
rows of the first one. A difference would appear only if a source removed rows in a later
download: the upsert updates existing rows but never deletes old ones, so the table would then
hold more rows than the last import reported.

**7. Countries without any life expectancy value (coverage gaps)**

32 countries have no WHO life expectancy:

American Samoa, Andorra, Aruba, Bermuda, British Virgin Islands, Cayman Islands, Channel Islands,
Curacao, Dominica, Faroe Islands, French Polynesia, Gibraltar, Greenland, Guam, Hong Kong SAR
(China), Isle of Man, Kosovo, Liechtenstein, Macao SAR (China), Marshall Islands, Monaco, Nauru
(listed by the World Bank as "Naoero"), New Caledonia, Northern Mariana Islands, Palau,
San Marino, Sint Maarten (Dutch part), St. Kitts and Nevis, St. Martin (French part),
Turks and Caicos Islands, Tuvalu, Virgin Islands (U.S.).

These are territories and very small states. WHO publishes its life expectancy estimates only
for its 194 member states, and some of these are not members or are too small to be estimated.
For several of them the OWID series can be used instead.

### Comparison with the source websites (Romania, 2023)

2023 is the latest year that all three sources share. The values were checked on the websites
on 2026-11-13.

| Source | Indicator | Stored value | Website | Result |
|---|---|---:|---|---|
| World Bank | Population ages 65 and above (% of total population) | 19.7531 | [data.worldbank.org](https://data.worldbank.org/indicator/SP.POP.65UP.TO.ZS?locations=RO) | matches (the website shows it rounded) |
| WHO GHO | Life expectancy at birth, both sexes (years) | 76.2 | [data.who.int](https://data.who.int/countries/642) | matches (the website shows it rounded) |
| Our World in Data | Life expectancy at birth (years) | 75.9381 | [ourworldindata.org](https://ourworldindata.org/grapher/life-expectancy?tab=table&time=2023&country=~ROU) | matches (the website shows it rounded) |

The stored values are the same as on the websites; the websites only show fewer decimals. The
two life expectancy values for Romania differ slightly (WHO 76.2, OWID 75.9) because the
sources use different estimates: OWID's series is based on the UN World Population Prospects,
WHO computes its own life tables.
