from gasstoragelevel.data_retrieval import fetch_gas_storage_levels, parse_gas_storage_data

SAMPLE_RESPONSE = {
    "last_page": 1,
    "data": [
        {"gasDayStart": "2026-04-01", "full": "21.83"},
        {"gasDayStart": "2026-01-15", "full": "45.25"},
        {"gasDayStart": "2025-12-31", "full": "60.50"},
        {"gasDayStart": "2025-04-01", "full": "29.14"},
        {"gasDayStart": "2025-04-02", "full": "-"},
    ],
}


def test_parse_gas_storage_data_returns_tidy_dataframe() -> None:
    df = parse_gas_storage_data(SAMPLE_RESPONSE)

    assert list(df.columns) == ["date", "gas_year", "fill_level_pct"]
    assert df["date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2025-04-01",
        "2025-12-31",
        "2026-01-15",
        "2026-04-01",
    ]
    assert df["fill_level_pct"].tolist() == [29.14, 60.50, 45.25, 21.83]
    assert df["gas_year"].tolist() == [
        "04/2025-03/2026",
        "04/2025-03/2026",
        "04/2025-03/2026",
        "04/2026-03/2027",
    ]


def test_fetch_gas_storage_levels_uses_api_key_and_paginates(monkeypatch) -> None:
    monkeypatch.setenv("AGSI_API_KEY", "test-key")
    requests_seen = []

    class Response:
        def __init__(self, page: int) -> None:
            self.page = page

        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {
                "last_page": 2,
                "data": [
                    {
                        "gasDayStart": f"2026-04-0{self.page}",
                        "full": str(20 + self.page),
                    }
                ],
            }

    def fake_get(url, *, params, headers, timeout):
        requests_seen.append((url, params.copy(), headers.copy(), timeout))
        return Response(params["page"])

    monkeypatch.setattr("gasstoragelevel.data_retrieval.agsi.requests.get", fake_get)

    df = fetch_gas_storage_levels(timeout=5)

    assert len(requests_seen) == 2
    assert requests_seen[0][2] == {"x-key": "test-key"}
    assert requests_seen[0][1]["country"] == "DE"
    assert [request[1]["page"] for request in requests_seen] == [1, 2]
    assert df["fill_level_pct"].tolist() == [21, 22]
