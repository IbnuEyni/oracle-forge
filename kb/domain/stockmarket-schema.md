# stockmarket Dataset — Schema and Domain Knowledge

## Overview

US publicly traded stocks and ETFs — metadata plus historical daily trading data. Two databases:

- **stockinfo_database (SQLite)** — stock/ETF metadata
- **stocktrade_database (DuckDB)** — historical daily prices for 2,753 securities

**Unique challenge:** DuckDB stores **one table per ticker symbol** (not a single trades table).

## Schema

### SQLite — stockinfo table (single table, metadata for all securities)

| Field | Type | Notes |
|---|---|---|
| Nasdaq Traded | str | Trading status |
| Symbol | str | Ticker symbol — matches DuckDB table name |
| Listing Exchange | str | NYSE, NASDAQ, etc. |
| Market Category | str | Market tier |
| ETF | str | Y/N flag |
| Round Lot Size | int | Standard trade size |
| Test Issue | str | Testing flag |
| Financial Status | str | Regulatory status |
| NextShares | str | NextShares flag |
| Company Description | str | Company description text |

### DuckDB — 2,753 separate tables (one per ticker symbol)

Each ticker has its own table named after the symbol (e.g., `AAPL`, `MSFT`, `TSLA`).

| Field | Type | Notes |
|---|---|---|
| Date | str/date | Trading date |
| Open | float | Opening price |
| High | float | Daily high |
| Low | float | Daily low |
| Close | float | Closing price |
| Adj Close | float | Adjusted close |
| Volume | int | Share volume traded |

## Authoritative Sources

- **Company metadata, listing info, descriptions** → SQLite `stockinfo`
- **Historical prices, volumes** → DuckDB `{SYMBOL}` table (one per ticker)

## Cross-Database Strategy

**Key insight:** To query price data for a specific stock, you must know the symbol first, then query the matching DuckDB table.

```python
import pandas as pd

# Step 1: Find the symbol from metadata
df_info = pd.read_sql("SELECT Symbol FROM stockinfo WHERE Company Description LIKE '%Apple%'", sqlite_conn)
symbol = df_info.iloc[0]['Symbol']  # e.g., 'AAPL'

# Step 2: Query the matching DuckDB table
df_prices = duckdb_conn.execute(f"SELECT * FROM {symbol}").df()
```

## Known Failure Patterns to Watch

1. **Table-per-ticker trap** — agent may look for a single `trades` or `prices` table in DuckDB. That does not exist. Each symbol is its own table.
2. **Symbol as table name** — queries must dynamically construct table names from the ticker symbol. Use parameterized table names safely (reject anything that is not a valid ticker).
3. **No ticker join** — there is no join column in DuckDB. The symbol IS the table name.
4. **Date format** — Date field is string, not DATE type. Use string comparison or parse.
5. **Adj Close vs Close** — for returns calculations, use `Adj Close` (adjusted for splits and dividends). For raw price, use `Close`.
6. **BIGINT/INT truncation on averages** — use `AVG(CAST(column AS FLOAT))` to avoid integer-truncated results (same pattern as Yelp).

## Query Volume

Check DAB — varies by dataset. Key queries involve finding specific tickers, then historical price analysis.
