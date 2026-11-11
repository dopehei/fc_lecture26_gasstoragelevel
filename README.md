# Gas Storage Level

Python package managed with [uv](https://docs.astral.sh/uv/).

## Setup

```sh
uv sync
```

## Checks

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
## Data retrieval

`gasstoragelevel.data_retrieval.fetch_gas_storage_levels()` downloads German gas storage
fill levels (Bundesnetzagentur / AGSI+) into a pandas DataFrame with the columns `date`,
`gas_year` and `fill_level_pct`. See `gas_analytics.ipynb` for usage.
