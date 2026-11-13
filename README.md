# Ageing Populations and Health Spending

A university project that imports public health data into a PostgreSQL database to explore whether countries with older populations spend more on health, and whether that spending helps people live longer and healthier lives.

The data comes from three sources, for every country, for the years 2000–2024:

| Source | Indicators |
|---|---|
| [World Bank Indicators API](https://api.worldbank.org/v2/) | population ages 65+ (%), GDP per capita (US$), hospital beds (per 1,000 people), and the country list |
| [WHO Global Health Observatory](https://www.who.int/data/gho) (OData API) | health expenditure per capita (US$), health expenditure (% of GDP), out-of-pocket expenditure (%), life expectancy at birth, healthy life expectancy (HALE) |
| [Our World in Data](https://ourworldindata.org/) | life expectancy at birth (long series) |

All sources and indicators are listed in [`etl/config.py`](etl/config.py).

## Requirements

- Python 3.11 or newer (developed with 3.14)
- PostgreSQL (developed with 18)
- Git
- An internet connection for the download step

## 1. Get the code

```bash
git clone https://github.com/Alverot/Ageing-Populations-and-Health-Spending.git
cd Ageing-Populations-and-Health-Spending
```

## 2. Install PostgreSQL and create the database

**Linux:** install PostgreSQL from your distribution's packages and start it, for example:

```bash
# Arch / Omarchy
sudo pacman -S postgresql
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl enable --now postgresql

# Debian / Ubuntu (the service starts on its own)
sudo apt install postgresql
```

Then open `psql` as the `postgres` superuser:

```bash
sudo -u postgres psql
```

**Windows:** install PostgreSQL with the installer from
[postgresql.org/download/windows](https://www.postgresql.org/download/windows/) (or from the ZIP
archive, as in Lab 1) and remember the password you choose for the `postgres` user. Then open
`psql` from a terminal (Command Prompt or PowerShell):

```powershell
psql -U postgres
```

If `psql` is not found, add PostgreSQL's `bin` folder (for example
`C:\Program Files\PostgreSQL\18\bin`) to your `PATH`.

**Both:** in `psql`, create the user and the database (choose your own password):

```sql
CREATE USER gh_user WITH PASSWORD 'change_me';
CREATE DATABASE global_health OWNER gh_user;
\q
```

## 3. Set up Python

Create a virtual environment and install the packages:

```bash
# Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Windows, if PowerShell refuses to run `Activate.ps1`, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt with
`.venv\Scripts\activate.bat`.

All the commands below are run from the project root folder with the virtual environment active.

## 4. Configure the database connection

Copy `.env.example` to `.env`:

```bash
cp .env.example .env        # Linux
copy .env.example .env      # Windows
```

Then open `.env` and replace `change_me` with the password you chose in step 2. The `.env` file
is git-ignored, so the password is never committed.

## 5. Create the tables

The tables are created and changed with [Alembic](https://alembic.sqlalchemy.org/) migrations
(folder [`migrations/versions/`](migrations/versions/)):

```bash
alembic upgrade head
```

This creates the five tables `source`, `country`, `indicator`, `observation` and `import_log`.
Run the same command again after pulling new migrations. `alembic current` shows the version the
database is at.

## 6. Download the data (extract)

```bash
python -m etl.extract
```

This downloads the World Bank country list and every indicator in `etl/config.py` and saves the
raw responses, unchanged, in `data/raw/who/`, `data/raw/worldbank/` and `data/raw/owid/`
(git-ignored). Each raw file gets a `<name>.source.json` next to it with the download URL and
time. It takes a few minutes.

The extractors can also be called one by one from a Python shell or a notebook, for example:

```python
from etl.extract_who import download_who_indicator
download_who_indicator("WHOSIS_000001")
```

## 7. Import the data into the database

Run the three imports in this order. The World Bank import must run first: it fills the
`country` table, and the other two use it to keep only real countries.

```bash
python -m etl.import_worldbank
python -m etl.import_who
python -m etl.import_owid
```

Each import transforms the saved files, cleans them (see [`etl/clean.py`](etl/clean.py)), saves
them with an upsert and writes one row per indicator to `import_log`. It prints one line per
indicator, for example:

```
SH.MED.BEDS.ZS           raw=  6650 rejected=  3705 inserted=  2945 updated=     0
```

- `rejected`: rows removed by the cleaning rules (regions instead of countries, empty values,
  years outside 2000–2024, impossible values, duplicates). The log lines above it say how many
  rows each rule removed.
- `inserted` / `updated`: the imports can be run again safely. Existing rows are updated instead
  of duplicated, so a second run shows `inserted=0`.

## 8. Check the data

Connect to the `global_health` database with DBeaver, pgAdmin or `psql`, for example:

```sql
SELECT i.code, COUNT(*) AS rows, MIN(o.year), MAX(o.year)
FROM observation o JOIN indicator i USING (indicator_id)
GROUP BY i.code ORDER BY i.code;
```

All the data quality queries and their results are in
[`docs/lab2_results.md`](docs/lab2_results.md).

## 9. Explore the raw data (optional)

```bash
jupyter notebook notebooks/lab2_exploration.ipynb
```

The notebook downloads and transforms every indicator and shows the share of missing values.

## Project structure

```
app/            database connection (database.py) and SQLAlchemy models (models.py)
etl/            the data pipeline
  config.py       sources, indicators and the year window
  extract*.py     download the raw data
  transform_*.py  turn raw files into the table country_iso3, indicator_code, year, sex, value
  clean.py        cleaning rules and the IQR outlier flag
  load.py         upserts and import_log
  import_*.py     one import script per source
migrations/     Alembic migrations
db/             Lab 1 schema (schema.sql) and schema dump
data/raw/       downloaded files (git-ignored)
docs/           architecture diagram, lab results, prompts used with AI assistants
notebooks/      Jupyter notebooks
```

## Adding a new indicator or source

- **New indicator from an existing source:** add it to `INDICATORS` in `etl/config.py`, then run
  the extract and the import again.
- **New source:** add it to `SOURCES` in `etl/config.py`, write `etl/extract_<source>.py` and
  `etl/transform_<source>.py`, register the extractor in `_DOWNLOADERS` in `etl/extract.py` and
  its raw file name in `_RAW_FILES` in `etl/import_common.py`, and add an
  `etl/import_<source>.py` script like the existing ones.
