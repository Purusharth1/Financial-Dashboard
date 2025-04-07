# Project Architecture

The **Financial Dashboard** project uses a modular architecture to integrate AI, external APIs, and user queries efficiently. Below is the system workflow.

## System Workflow

```mermaid
graph TD;
    A[User Query] -->|Input| B[LangChain Agent];
    B -->|Tool Selection| C[Financial Tools];
    C -->|Crypto API| D[CoinGecko];
    C -->|Stock API| E[yfinance];
    C -->|Loan Calc| F[Loan EMI Calculator];
    C -->|Investment Calc| G[Investment Return];
    C -->|Emergency Fund| H[Emergency Fund Calc];
    D -->|Price Data| I[Response Formatter];
    E -->|Price Data| I;
    F -->|EMI Details| I;
    G -->|Returns| I;
    H -->|Fund Size| I;
    I -->|Output| J[User Response];
```

## Components

- **User Query**: Natural language input (e.g., "What's the current price of Bitcoin?").
- **LangChain Agent**: AI agent using Ollama to interpret queries and select tools.
- **Financial Tools**:
  - **CoinGecko API**: Fetches crypto prices (current and historical).
  - **yfinance**: Fetches stock prices (current and historical).
  - **Loan EMI Calculator**: Calculates loan EMIs based on principal, interest rate, and tenure.
  - **Investment Return**: Calculates investment returns.
  - **Emergency Fund Calc**: Estimates emergency fund size.
- **Response Formatter**: Formats outputs with timestamps.

---

## Next Steps

- [Features](features.md)
- [Installation Guide](installation.md)