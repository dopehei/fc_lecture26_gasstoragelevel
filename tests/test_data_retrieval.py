from gasstoragelevel.data_retrieval import parse_gas_storage_csv

SAMPLE_CSV = (
    "                    .;04/2025-03/2026;04/2026-03/2027\r\n"
    "01.04.;29,14;21,83\r\n"
    "31.12.;60,50;\r\n"
    "15.01.;45,25;\r\n"
)


def test_parse_gas_storage_csv_returns_tidy_dataframe() -> None:
    df = parse_gas_storage_csv(SAMPLE_CSV)

    assert list(df.columns) == ["date", "gas_year", "fill_level_pct"]
    assert df["date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2025-04-01",
        "2025-12-31",
        "2026-01-15",
        "2026-04-01",
    ]
    assert df["fill_level_pct"].tolist() == [29.14, 60.50, 45.25, 21.83]
    assert df["gas_year"].tolist()[-1] == "04/2026-03/2027"
