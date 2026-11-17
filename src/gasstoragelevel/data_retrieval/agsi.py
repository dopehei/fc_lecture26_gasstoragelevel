"""Retrieve German gas storage fill levels from the AGSI API."""

import os
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import requests

AGSI_API_URL = "https://agsi.gie.eu/api"
AGSI_API_KEY_PATH = Path(__file__).resolve().parents[3] / ".agsi_api_key"
DATAFRAME_COLUMNS = ["date", "gas_year", "fill_level_pct"]
API_PAGE_SIZE = 300


def parse_gas_storage_data(payload: dict[str, Any]) -> pd.DataFrame:
    """Parse AGSI API data into a tidy DataFrame sorted by date.

    Returns the columns ``date`` (datetime64), ``gas_year`` (e.g.
    ``"04/2025-03/2026"``) and ``fill_level_pct`` (float). Days without a
    published fill level are dropped.
    """
    records = pd.DataFrame(payload.get("data", []))
    if records.empty:
        return pd.DataFrame(columns=DATAFRAME_COLUMNS)

    records["date"] = pd.to_datetime(records["gasDayStart"], errors="coerce")
    records["fill_level_pct"] = pd.to_numeric(records["full"], errors="coerce")
    records = records.dropna(subset=["date", "fill_level_pct"])

    gas_year_start = records["date"].dt.year - records["date"].dt.month.lt(4).astype(int)
    records["gas_year"] = gas_year_start.map(lambda year: f"04/{year}-03/{year + 1}")

    return records[DATAFRAME_COLUMNS].sort_values("date").reset_index(drop=True)


def _read_api_key() -> str:
    key = os.environ.get("AGSI_API_KEY")
    if key is None:
        try:
            key = AGSI_API_KEY_PATH.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise RuntimeError(
                "Set AGSI_API_KEY or add your key to the ignored .agsi_api_key file."
            ) from error

    key = key.strip()
    if not key:
        raise RuntimeError("The AGSI API key is empty.")
    return key


def fetch_gas_storage_levels(url: str = AGSI_API_URL, timeout: float = 30.0) -> pd.DataFrame:
    """Download Germany's AGSI fill-level history as a DataFrame."""
    headers = {"x-key": _read_api_key()}
    params: dict[str, str | int] = {
        "country": "DE",
        "from": "2016-01-01",
        "to": date.today().isoformat(),
        "size": API_PAGE_SIZE,
        "page": 1,
    }
    payload: dict[str, Any] = {"data": []}

    while True:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        page = response.json()
        payload["data"].extend(page.get("data", []))

        last_page = int(page.get("last_page", 1))
        if params["page"] >= last_page:
            break
        params["page"] += 1

    return parse_gas_storage_data(payload)
