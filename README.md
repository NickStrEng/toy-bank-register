# Quick Start Guide

Get the Bank Management Application running using **uv**

## Prerequisites

Before starting, verify you have:
- Python 3.14 installed (`python3 --version`)
- SQL Server running (Docker or local)
- Git installed - `git --version`

## Setup

### 1. Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
```

### 2. Clone repository from GitHub


```bash
# Clone from GitHub
git clone https://github.com/NickStrEng/toy-bank-register.git

# Navigate to project directory
cd toy-bank-register
```

## 3. Set up virtual environment and install dependencies

```bash
# uv automatically reads pyproject.toml and installs packages
uv sync
```

This command:
- Creates virtual environment in `.venv/`
- Installs all dependencies from `pyproject.toml`
- Creates/updates `uv.lock` for reproducible builds

### 5. Configure MSSQL database

Create `.env` file at root level:
```bash
# .env
DB_SERVER=localhost,1433
DB_NAME=BanksDB
DB_USER=SA
DB_PASSWORD=<your-password>
SECRET_KEY=<your-api-secret-key>
```
If in local MS SQL Server, create new database `BanksDB` and set the server port to 1433.

If from Docker image:
1. initialise container with MS SQL Server 2022 image:
```bash
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=<your-password>" -e "MSSQL_PID=Developer" -e "MSSQL_USER=SA" -p 1433:1433 --name sql2022 --hostname sql2022 -d  mcr.microsoft.com/mssql/server:2022-latest
```
2. install MS ODBC 18 driver:
https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver17

3. execute an interactive bash session within the container
```bash
docker exec -it sql2022 /bin/bash 
```
4. connect to SQL Server:
```bash
/opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P "<your-password>" -C
```
5. create database `BanksDB` via terminal SQL:
```bash
CREATE DATABASE BanksDB;
GO
```

### 6. Run the application

**Run Flask app:**
```bash
# uv automatically activates the virtual environment
uv run python app.py
```

Visit: **http://localhost:5000**

## Verify Installation

### Test Web Interface
1. Open browser to `http://localhost:5000`
2. Click "Add New Bank"
3. Fill in form and submit
4. Verify bank appears in list

### Test API
```bash
# Get all banks
curl http://localhost:5001/api/banks

# Create a bank
curl -X POST http://localhost:5001/api/banks \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Bank","location":"Test City"}'
```

### Run Tests
```bash
# Run all tests with uv
uv run pytest
```

### Running Scripts
```bash
# Run Python script with uv (auto-activates venv)
uv run python app.py
```

## 📁 Complete Project Structure

```
toy-bank-register/
│
├── .venv/                      # Virtual environment (auto-created by uv)
├── .env                        # Environment variables (create this)
├── .python-version             # Python version (auto-created by uv)
├── pyproject.toml              # Project config & dependencies
├── uv.lock                     # Locked dependencies (auto-created)
│
├── app.py                      # Flask application
├── api_client.py               # RESTful API client
├── test_app.py                 # PyTest unit tests
├── README.md                   # Documentation
│
└── templates/                  # Bootstrap HTML templates
    ├── base.html
    ├── index.html
    ├── view_bank.html
    ├── create_bank.html
    └── edit_bank.html
```

### Try the API Client
```bash
# Demonstration mode
uv run python api_client.py
```
