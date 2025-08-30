# data_ingest/fetch_portfolio.py
from pathlib import Path
import csv
from typing import List, Dict, Any, Optional
import requests
from .utils import LOG, DATA_DIR


def load_portfolio_from_csv(csv_path: Path) -> List[Dict[str, Any]]:
    """Load a portfolio CSV with headers like: symbol, quantity, avg_price, instrument_type"""
    LOG.info(f"Loading portfolio from CSV: {csv_path}")
    positions = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                row["quantity"] = float(row.get("quantity", 0) or 0)
            except Exception:
                row["quantity"] = 0
            try:
                row["avg_price"] = float(row.get("avg_price", 0) or 0)
            except Exception:
                row["avg_price"] = 0
            positions.append(row)
    LOG.info(f"Loaded {len(positions)} positions")
    return positions


def fetch_portfolio_from_api(api_url: str, api_key: Optional[str] = None, timeout: int = 10) -> List[Dict[str, Any]]:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    LOG.info(f"Fetching portfolio from API: {api_url}")
    resp = requests.get(api_url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    positions = data.get("positions") or data.get("portfolio") or data
    if isinstance(positions, dict):
        positions = positions.get("positions") or positions.get("items") or [positions]
    LOG.info(f"API returned {len(positions) if hasattr(positions, '__len__') else 'unknown'} positions")
    return positions


def mock_portfolio(user_id: str = "demo") -> List[Dict[str, Any]]:
    LOG.info(f"Generating mock portfolio for user: {user_id}")
    return [
        {"symbol": "RELIANCE.NS", "quantity": 10, "avg_price": 2400.0, "instrument_type": "EQUITY"},
        {"symbol": "HDFCBANK.NS", "quantity": 5, "avg_price": 1600.0, "instrument_type": "EQUITY"},
        {"symbol": "ICICI.NS", "quantity": 8, "avg_price": 900.0, "instrument_type": "EQUITY"},
    ]


def ingest_portfolio_and_save(portfolio: List[Dict[str, Any]], filename: str = "portfolio.json") -> Path:
    path = DATA_DIR / filename
    from .utils import save_json

    save_json({"positions": portfolio}, path)
    return path
