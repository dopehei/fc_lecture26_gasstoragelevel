"""Retrieve German gas storage fill levels published by the Bundesnetzagentur.

The data shown on
https://www.bundesnetzagentur.de/DE/Gasversorgung/aktuelle_gasversorgung/_svg/Gasspeicher_Fuellstand/Speicherfuellstand.html
originates from AGSI+ and is offered as a CSV export. The CSV has one row per
calendar day ("dd.mm.") and one column per gas storage year (April - March),
with fill levels in percent using German decimal notation.
"""

import io

import pandas as pd
import requests

BNETZA_CSV_URL = (
    "https://www.bundesnetzagentur.de/SiteGlobals/Functions/SVG/_functions/"
    "csv_export.html?view=renderCSV&id=870304"
)


def parse_gas_storage_csv(csv_text: str) -> pd.DataFrame:
    """Parse the Bundesnetzagentur CSV export into a tidy DataFrame.

    Returns a DataFrame with the columns ``date`` (datetime64), ``gas_year``
    (e.g. ``"04/2025-03/2026"``) and ``fill_level_pct`` (float), sorted by date.
    Days without a published value are dropped.
    """
    wide = pd.read_csv(io.StringIO(csv_text), sep=";", decimal=",", dtype={0: str})
    wide = wide.rename(columns={wide.columns[0]: "day"})
    wide["day"] = wide["day"].str.strip()

    long = wide.melt(id_vars="day", var_name="gas_year", value_name="fill_level_pct")
    long["fill_level_pct"] = pd.to_numeric(long["fill_level_pct"], errors="coerce")
    long = long.dropna(subset=["fill_level_pct"])

    # Gas year "04/YYYY-03/ZZZZ": April-December belong to YYYY, January-March to ZZZZ.
    years = long["gas_year"].str.extract(r"(\d{4})-\d{2}/(\d{4})").astype(int)
    day_month = long["day"].str.extract(r"(\d{2})\.(\d{2})").astype(int)
    year = years[0].where(day_month[1] >= 4, years[1])
    long["date"] = pd.to_datetime(
        {"year": year, "month": day_month[1], "day": day_month[0]}, errors="coerce"
    )

    return (
        long.dropna(subset=["date"])[["date", "gas_year", "fill_level_pct"]]
        .sort_values("date")
        .reset_index(drop=True)
    )


def fetch_gas_storage_levels(url: str = BNETZA_CSV_URL, timeout: float = 30.0) -> pd.DataFrame:
    """Download the current gas storage fill levels for Germany as a DataFrame.

    See :func:`parse_gas_storage_csv` for the structure of the returned DataFrame.
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"
    return parse_gas_storage_csv(response.text)
