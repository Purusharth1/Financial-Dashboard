# Usage Guide

This guide explains how to use the **Financial Dashboard** with natural language queries.

## Query Examples

### Current Price Queries
- "What is the current price of Bitcoin?"
- "Show me Ethereum's market value."
- "Get the latest price of Dogecoin."
- "What is the current price of Apple stock?"

### Historical Price Queries
- "How much did Solana price increase from 2023-01-01 to 2023-12-31?"
- "What's the price growth of AAPL from 2022-01-01 to 2023-01-01?"

### Investment Calculations
- "If I invested $1000 in Bitcoin on 2023-01-01, what would it be worth now?"
- "Calculate returns on $500 invested in AAPL in 2022."

### Spending Analysis
- "Show me my spending breakdown for 2023."

### Emergency Fund
- "What's the recommended emergency fund size for $2000 monthly expenses?"

## Steps to Use

1. Run the application:
   ```bash
   uv run llm/query_llm.py
   ```
2. Enter your query in the terminal or script interface.
3. Review the response, including timestamps for current data.

## Troubleshooting

- **No Data**: Ensure internet connectivity; yfinance and CoinGecko require it.
- **Format Errors**: Use `YYYY-MM-DD` for dates.
- **Slow Response**: Check API rate limits or network latency.

---

## Next Steps

- [API Documentation](api.md)
- [Testing Results](testing.md)