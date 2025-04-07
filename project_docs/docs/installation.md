# Installation Guide

Follow these steps to set up the **Financial Dashboard** project locally.

## Prerequisites

- **Python**: 3.8 or higher
- **Git**: For cloning the repository
- **No API Keys Required**: CoinGecko and yfinance are free and don't need keys.
- **Ollama**: For hosting the model
- **Just**: For JustFile


## Step 1: Clone the Repository

```bash
git clone https://github.com/Purusharth1/Financial-Dashboard.git
cd Financial-Dashboard
```

## Step 2: Install Dependencies

Install required Python libraries:

```bash
just setup
```

Key dependencies:

- `langchain`
- `langchain-ollama`
- `requests`
- `yfinance`
- `pydantic`
- `loguru`

## Step 3: Run the Application

Start the dashboard:

```bash
just run-query
```

---

## Next Steps

- [Usage Guide](usage.md)
- [API Documentation](api.md)