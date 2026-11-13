"""Every data source and indicator the import pipeline uses.

To change where an indicator comes from, or to add a new one, edit this file.
A new source also needs an extractor in etl/extract_<source>.py (downloads
and saves the raw data) and a transform in etl/transform_<source>.py (turns
the raw file into the normalized table: country_iso3, indicator_code, year,
sex, value).
"""

# Years kept for the study; the extractors download this window and the
# cleaning step drops anything outside it.
YEAR_FROM = 2000
YEAR_TO = 2024

# "url" is the link saved in the source table;
# "api_url" is where the extractor downloads the data from.

SOURCES = {
    "who": {
        "name": "WHO Global Health Observatory (GHO) OData API",
        "url": "https://ghoapi.azureedge.net/api/",
        "api_url": "https://ghoapi.azureedge.net/api",
    },
    "world_bank": {
        "name": "World Bank Indicators API",
        "url": "https://api.worldbank.org/v2/",
        "api_url": "https://api.worldbank.org/v2",
    },
    "owid": {
        "name": "Our World in Data",
        "url": "https://ourworldindata.org/",
        "api_url": "https://ourworldindata.org/grapher",
    },
}

INDICATORS = [
    {
        "code": "SP.POP.65UP.TO.ZS",
        "name": "Population ages 65 and above",
        "unit": "% of total population",
        "source": "world_bank",
    },
    {
        "code": "NY.GDP.PCAP.CD",
        "name": "GDP per capita",
        "unit": "current US$",
        "source": "world_bank",
    },
    {
        "code": "SH.MED.BEDS.ZS",
        "name": "Hospital beds",
        "unit": "per 1,000 people",
        "source": "world_bank",
    },
    {
        "code": "GHED_CHE_pc_US_SHA2011",
        "name": "Current health expenditure per capita",
        "unit": "current US$",
        "source": "who",
    },
    {
        "code": "GHED_CHEGDP_SHA2011",
        "name": "Current health expenditure",
        "unit": "% of GDP",
        "source": "who",
    },
    {
        "code": "GHED_OOPSCHE_SHA2011",
        "name": "Out-of-pocket expenditure",
        "unit": "% of current health expenditure",
        "source": "who",
    },
    {
        "code": "WHOSIS_000001",
        "name": "Life expectancy at birth",
        "unit": "years",
        "source": "who",
    },
    {
        "code": "WHOSIS_000002",
        "name": "Healthy life expectancy (HALE) at birth",
        "unit": "years",
        "source": "who",
    },
    {
        "code": "life-expectancy",
        "name": "Life expectancy at birth (long series)",
        "unit": "years",
        "source": "owid",
    },
]
