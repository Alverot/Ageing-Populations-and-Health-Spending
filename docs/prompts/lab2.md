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
