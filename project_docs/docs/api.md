# API Documentation

The **Financial Dashboard** is primarily a command-line tool but could be extended with an API. Below is a hypothetical API setup using FastAPI.

## API Endpoints (Hypothetical)

### 1. Get Current Price
- **Endpoint**: `/current_price`
- **Method**: `POST`
- **Description**: Fetches the current price of a crypto or stock.
- **Request Body**:
  ```json
  {
    "asset_id": "Bitcoin",
    "asset_type": "crypto",
    "vs_currency": "usd"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "asset_id": "Bitcoin",
      "asset_type": "crypto",
      "current_price": 79026.43,
      "timestamp": "2025-04-07 15:52:00 UTC"
    }
  }
  ```

## Running the API (Future Extension)

Start a FastAPI server (not currently implemented):

```bash
uvicorn app.api.server:app --reload
```

---

## Next Steps

- [Installation Guide](installation.md)
- [Testing Results](testing.md)