set shell := ["bash", "-cu"]
set dotenv-load

default:
  just --list

# Setup environment and install dependencies
setup:
  uv sync

# Start the FastAPI financial API server
start-api-server:
  uv run api/financial_api.py

# Run the LLM query module
run-llm:
  uv run llm/query_llm.py

# Start logging server
start-logging-server:
  uv run python -m utils.logging_server

# Start the Streamlit frontend
start-frontend-server:
  uv run streamlit run ui/app.py

# Start all servers (background mode with logging)
run-query:
  @echo "Starting all servers..."
  @echo "Starting logging server..."
  uv run python -m utils.logging_server > logging_server.log 2>&1 &
  @echo "Starting API server..."
  uv run api/financial_api.py > backend_api.log 2>&1 &
  @echo "Starting frontend server..."
  uv run streamlit run ui/app.py > frontend_server.log 2>&1 &
  @echo "All servers started! Check respective log files for details."
  @echo "To stop all servers, use: just stop-all"

# Stop all running servers
stop-all:
  echo "Stopping all servers..."
  pkill -f "uv run python -m utils.logging_server" || true
  pkill -f "uv run api/financial_api.py" || true
  pkill -f "uv run streamlit run frontend.py" || true
  echo "All servers stopped."

# View MkDocs documentation
documentation:
  uv run mkdocs serve --config-file project_docs/mkdocs.yml

# Run Locust load testing
load-testing:
  uv run locust -f locustfile.py --host=http://127.0.0.1:8000