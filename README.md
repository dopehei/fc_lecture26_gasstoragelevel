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
fill levels from the AGSI API into a pandas DataFrame with the columns `date`, `gas_year`
and `fill_level_pct`. Set the `AGSI_API_KEY` environment variable or put the key in the
root-level `.agsi_api_key` file, which is excluded by `.gitignore`. Credit GIE / AGSI as
the data source when publishing these data. See `gas_analytics.ipynb` for usage.
