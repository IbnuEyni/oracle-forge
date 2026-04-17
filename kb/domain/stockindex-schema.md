# stockindex Dataset — Schema and Domain Knowledge

## Overview

Stock market indices from major exchanges worldwide — metadata plus daily price data. Two databases:

- **indexinfo_database (SQLite)** — exchange metadata
- **indextrade_database (DuckDB)** — daily index price history

**Simpler than stockmarket** — single `index_trade` table, not one-table-per-ticker.

## Schema

### SQLite — index_info table

| Field | Type | Notes |
|---|---|---|
| Exchange | str | Exchange name (NYSE, LSE, TSE, etc.) |
| Currency | str | Trading currency (USD, GBP, JPY, etc.) |

### DuckDB — index_trade table

| Field | Type | Notes |
|---|---|---|
| Index | str | Index name/symbol |
| Date | str | Trading date |
| Open | float | Opening price |
| High | float | Daily high |
| Low | float | Daily low |
| Close | float | Closing price |
| Adj Close | float | Adjusted close |
| CloseUSD | float | Close value converted to USD |

## Authoritative Sources

- **Exchange and currency info** → SQLite `index_info`
- **Daily prices, USD-converted values** → DuckDB `index_trade`

## Cross-Database Strategy

Query each separately. The join is on **Exchange** or **Index name** depending on query context.

```python
# SQLite side
df_info = pd.read_sql("SELECT * FROM index_info WHERE Currency = 'USD'", sqlite_conn)

# DuckDB side
df_prices = duckdb_conn.execute("SELECT * FROM index_trade WHERE Date >= '2020-01-01'").df()
```

## Key Distinction: Close vs CloseUSD

- **Close** — price in native currency of the exchange
- **CloseUSD** — price converted to USD

**RULE:** For cross-country comparisons or USD-denominated analysis, use `CloseUSD`. For raw index level in local terms, use `Close`.

## Known Failure Patterns to Watch

1. **Currency confusion** — comparing raw `Close` values across different exchanges is meaningless (apples to oranges). Use `CloseUSD` for cross-index comparison.
2. **No trade-per-symbol tables** — unlike stockmarket dataset, all indices are in ONE table (`index_trade`). Filter by `Index` column.
3. **Date format** — string, not DATE type. Use string comparison.
4. **Adj Close vs Close** — same rule as stocks. Use Adj Close for return calculations.
5. **BIGINT/INT truncation** — cast to FLOAT before AVG.

## Query Volume

Check DAB — moderate. Queries typically involve cross-exchange comparison, time-range analysis, or currency-normalized performance.
