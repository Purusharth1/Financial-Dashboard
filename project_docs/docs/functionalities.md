# 📦 Financial Dashboard Installation Guide

Welcome to the **Financial Dashboard** project. This guide walks you through setting up and running the system for financial data exploration powered by modern APIs and LLM integration.

## Prerequisites

Ensure the following tools are installed:

1. **Python 3.12**
   - [Download Python](https://www.python.org/downloads/)

2. **`just` command runner**
   ```bash
   sudo apt install just
   ```

3. **`uv` package/environment manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

## Installation Steps

### Step 1: Environment Setup

Set up your Python environment and install dependencies with:

```bash
just setup
```

This will:
- Create the Python virtual environment
- Install all required dependencies

### Step 2: Running the Project

#### Start All Services

Launch backend, UI, and any additional modules with:

```bash
just start-all
```

Logs will be saved in the root directory for each module. To stop everything:

```bash
just stop-all
```

#### Start Individual Services

```bash
just start-api     # FastAPI backend
just start-ui      # UI frontend
```

### Step 3: Load Testing (Optional)

Run Locust-based performance tests:

```bash
just load_testing
```

Open [http://localhost:8089](http://localhost:8089) to configure and monitor user load.

## Access Points

- **Frontend Interface**: `http://localhost:7860/`
- **API Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`

## API Quick Reference

- `/api/query/ask-llm`: Ask financial questions via LLM
- `/api/data/ingest`: Upload and process financial data

## Testing Flow

1. Start backend and UI
2. Ingest a dataset
3. Ask a financial question using the LLM interface
4. Review responses and visualizations
5. Test API under load with Locust