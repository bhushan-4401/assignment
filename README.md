# Excel Query Bot

AI-powered app for querying Excel data using natural language. Upload your Excel files and ask questions in plain English.

## Features

- Natural language to SQL conversion using Azure OpenAI GPT-4o
- Excel file processing and data cleaning
- Interactive web interface with Streamlit
- Export results as CSV
- PostgreSQL backend

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- Azure OpenAI API access

### Setup

1. **Install dependencies**
```bash
conda env create -f environment.yml
conda activate app
```

2. **Configure database**
```sql
CREATE DATABASE test;
```

3. **Set up config files**
```bash
cp config/config.toml.example config/config.toml
cp config/.secrets.toml.example config/.secrets.toml
```

4. **Update config/config.toml**
```toml
[RDBMS]
USERNAME = "your_username"
HOST = "localhost"
PORT = 5432
DATABASE_NAME = "test"

[GENERATOR]
AZURE_ENDPOINT = "your_azure_endpoint"
AZURE_DEPLOYMENT = "your_deployment_name"
OPENAI_API_VERSION = "openai_api_version"
```

5. **Update config/.secrets.toml**
```toml
[RDBMS_PASSWORD]
PASSWORD = "your_db_password"

[AZURE]
AZURE_GENERATOR_KEY = "your_azure_api_key"
```

### Run the App

```bash
streamlit run app.py
```

## Usage

1. Upload Excel file (.xlsx or .xls)
2. Ask questions like:
   - "What is the total revenue by month?"
   - "Show top 10 customers by sales"
   - "What's the average order value?"
3. Download results as CSV

## Architecture

```
Streamlit UI → Excel Processor → ReAct Agent → SQL Tool → PostgreSQL
                                     ↓
                              Azure OpenAI GPT-4o
```

**Key Components:**
- `ExcelProcessor` - Handles file upload and data cleaning
- `AppReact` - ReAct agent for natural language processing
- `SqlQueryTool` - Executes SQL queries
- `Database` - PostgreSQL interface

## Project Structure

```
src/
├── agents/          # ReAct workflow and SQL tools
├── core/           # Database and system prompts
├── file_processor/ # Excel processing
└── generator/      # Azure OpenAI integration
```

## Troubleshooting

**Database connection issues:**
- Check PostgreSQL is running
- Verify credentials in config files

**Azure OpenAI errors:**
- Validate API key and endpoint
- Check rate limits

**Excel processing errors:**
- Ensure valid Excel format
- Check for proper headers

## Dependencies

- Streamlit
- LangChain
- Azure OpenAI
- Pandas
- SQLAlchemy
- PostgreSQL drivers

---

Built with Azure OpenAI GPT-4o and PostgreSQL backend.