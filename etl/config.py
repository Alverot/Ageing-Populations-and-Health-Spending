"""Every data source and indicator the import pipeline uses.

To change where an indicator comes from, or to add a new one, edit this file.
A new source also needs one extractor that returns the normalized table:
country_iso3, indicator_code, year, sex, value.
"""

SOURCES = {
    "who_hdx": {
        "name": "WHO Global Health Observatory (via HDX)",
        "url": "https://data.humdata.org/organization/world-health-organization",
    },
    "world_bank": {
        "name": "World Bank Indicators API",
        "url": "https://api.worldbank.org/v2/",
    },
    "owid": {
        "name": "Our World in Data",
        "url": "https://ourworldindata.org/",
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
        "source": "who_hdx",
    },
    {
        "code": "GHED_CHEGDP_SHA2011",
        "name": "Current health expenditure",
        "unit": "% of GDP",
        "source": "who_hdx",
    },
    {
        "code": "GHED_OOPSCHE_SHA2011",
        "name": "Out-of-pocket expenditure",
        "unit": "% of current health expenditure",
        "source": "who_hdx",
    },
    {
        "code": "WHOSIS_000001",
        "name": "Life expectancy at birth",
        "unit": "years",
        "source": "who_hdx",
    },
    {
        "code": "WHOSIS_000002",
        "name": "Healthy life expectancy (HALE) at birth",
        "unit": "years",
        "source": "who_hdx",
    },
    {
        "code": "life-expectancy",
        "name": "Life expectancy at birth (long series)",
        "unit": "years",
        "source": "owid",
    },
]
