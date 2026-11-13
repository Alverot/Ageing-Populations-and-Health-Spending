# Lab 2 – Prompts

Every prompt sent to an AI assistant to generate or change code for Lab 2, in the order they were used.

## Prompt 1 – start Lab 2
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: no need for the backup i guess, push them now and lets start lab 2
- Result: the assistant read the Lab 2 brief, checked that the WHO GHO API works again and set up Alembic (`alembic.ini`, `migrations/env.py`, `migrations/versions/0001_baseline.py`). No commit yet; the files were committed after Prompt 4.
- Your changes: TODO

## Prompt 2 – list of Lab 2 tasks
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: before we get to work make me a list with all the stuff we need to do, its ok if alredy did some stuff
- Result: a checklist of the Lab 2 tasks and the teacher's extra requests. No code changed.
- Your changes: TODO

## Prompt 3 – discuss decisions
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: ok, continue but please talk to me dont make decisions on your own, discuss with me
- Result: the assistant listed the open decisions for the Alembic step (folder name, baseline and stamp, requirements, `app/create_tables.py`, commit message). No code changed.
- Your changes: TODO

## Prompt 4 – Alembic decisions
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt:
  > 1. migrations its fine
  > 2. ok good
  > 3. yes without the version number
  > 4. your recomandation
  > 5. delete it
  > 6. ok yea its fine this way
  > 7. yep commit
- Result: `alembic` added to `requirements.txt`, `app/create_tables.py` removed (Alembic now creates the tables), the generated `migrations/README` deleted, this prompts file started. Commit "Lab 2: Alembic setup with baseline migration".
- Your changes: TODO

## Prompt 5 – WHO source
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: (answer to the assistant's question whether to use the WHO GHO API, which worked again, or keep the WHO CSV files from HDX) WHO API (Recommended)
- Result: WHO data is now downloaded from the GHO OData API instead of HDX. Commit "Lab 2: Raw data extractors (WHO, World Bank, OWID)".
- Your changes: TODO

## Prompt 6 – source settings in etl/config.py
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt:
  > Small thing remember that we need to use data from at least 2 sources with the posibility in the future to be easy to conect more. Also o dont whant to have data only for romania, the point is to be able to compare more countries
  > 3.a go with who
  > 3.b ok
  > 3.c sure
  > 3.d idk its some small changes i whink its ok if they go this time in the same commit
- Result: in `etl/config.py` the source key `who_hdx` became `who`, with the GHO API name and link, and the comment at the top explains how to add a new source. Commit "Lab 2: Raw data extractors (WHO, World Bank, OWID)".
- Your changes: TODO

## Prompt 7 – commit and push plan
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: A, and we push everything at the end
- Result: the `config.py` change goes in the extractors commit; everything is pushed at the end of the lab. No code changed.
- Your changes: TODO

## Prompt 8 – extractors
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt:
  > 5.a follow the reference structure, but make the changes in 5b and 5c
  > 5.b go with you sugestion
  > 5.c ok
  > 5.d ok do that
  > 5.e good then one commit
- Result: `etl/raw_files.py`, `etl/json_types.py`, `etl/extract_who.py`, `etl/extract_worldbank.py`, `etl/extract_owid.py` and `etl/extract.py` (`download_all()`, run with `python -m etl.extract`). The structure follows the lab's reference repository (github.com/feliciacricri/global-health-app), with two changes: the API addresses are read from `"api_url"` in `etl/config.py` instead of being written in each extractor, and the year window (`YEAR_FROM = 2000`, `YEAR_TO = 2024`) is defined once in `etl/config.py`. Commit "Lab 2: Raw data extractors (WHO, World Bank, OWID)".
- Your changes: TODO

## Prompt 9 – transforms
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: keep it and start the transforms
- Result: hospital beds (`SH.MED.BEDS.ZS`, 45% missing values) stays in the indicator list. New `etl/transform_who.py`, `etl/transform_worldbank.py` and `etl/transform_owid.py`, following the lab's reference repository; tested on the downloaded files. Commit "Lab 2: Raw-to-DB transform modules".
- Your changes: TODO

## Prompt 10 – cleaning
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: yes commit and start the cleaning
- Result: `etl/clean.py` with the cleaning rules from the lab and the IQR outlier flag (Task 2.2), the `Sex` enum and the `is_outlier` column in `app/models.py`, and the Alembic migration `migrations/versions/0002_observation_is_outlier.py`. The assistant proposed plausible bounds for our nine indicators (the lab only gives bounds for its own). Commit "Lab 2: Observation cleaning module with IQR outlier flag".
- Your changes: TODO

## Prompt 11 – bounds approved
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: perfect lets continue
- Result: the proposed bounds were kept as they are. Commit "Lab 2: Observation cleaning module with IQR outlier flag".
- Your changes: TODO

## Prompt 12 – import_log row counts
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: Go with b
- Result: `etl/load.py` (upserts that count inserted and updated rows separately), `etl/import_common.py` (the import loop shared by the sources, reading the indicators from `etl/config.py`), `etl/import_worldbank.py`, `etl/import_who.py`, `etl/import_owid.py`, and the migration `migrations/versions/0003_import_log_row_counts.py`, which adds `rows_inserted`, `rows_updated` and `rows_rejected` to `import_log` (teacher's request to report imported and rejected rows). Commit "Lab 2: Observation loader and per-source import scripts".
- Your changes: TODO

## Prompt 13 – Task 2.1 notebook
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: yes commit and continue
- Result: `notebooks/lab2_exploration.ipynb`: calls each extractor, transforms the saved files, inspects one indicator per source with `head()`, `info()` and `isna().sum()`, and shows the share of missing values per indicator. The notes in section 5 were written by the assistant. Commit "Lab 2: Notebook exploring raw downloads and missing values".
- Your changes: TODO

## Prompt 14 – commit the notebook
- Tool and model: Claude Code, Claude Opus 5.5
- Date: 2026-11-13
- Prompt: yes commit
- Result: the notebook was committed as it was. Commit "Lab 2: Notebook exploring raw downloads and missing values".
- Your changes: TODO
