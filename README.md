# Data Profiling and Quality Assessment Using CrewAI

A Python-based workflow for profiling data and assessing data quality in SQLite databases, powered by **CrewAI**. This project automatically generates SQL queries for profiling, identifies data quality issues, and formats the results into a Markdown report.

---

## Features

- **Automated Schema Fetching**:
  - Uses `SQLiteSchemaTool` to extract table names and column metadata from a SQLite database.

- **Data Profiling**:
  - Generates SQL queries for profiling data, such as:
    - Counting records.
    - Summarizing categorical columns.
    - Calculating statistics for numerical columns.

- **Data Quality Checks**:
  - Identifies potential data quality issues like:
    - Missing values.
    - Duplicates.
    - Outliers.
    - Referential integrity violations.

- **Query Execution**:
  - Executes profiling and validation queries using `SQLiteQueryTool`.

- **Markdown Report Generation**:
  - Presents query results and findings in a structured Markdown report.

---

## Project Structure
├── database.db # SQLite database used for profiling 

├── dataset.csv # Sample dataset to load into SQLite 

├── profile.yaml # Profiling SQL queries output 

├── dq.yaml # Data quality queries output 

├── results.yaml # Query results output 

├── report.md # Final Markdown report 

├── dq_profile.py # Main script 

└── README.md # This file


---

## Setup

### Prerequisites
- Python 3.8 or higher
- Required libraries: `pandas`, `sqlite3`, `crewai`, `openai`

Install the required dependencies:
```bash
pip install pandas sqlite3 crewai openai
```

### Environment Variables
Set up the OpenAI API Key as an environment variable:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

##How to Use

### Step 1: Prepare the SQLite Database

Convert your CSV file to an SQLite database:
```bash
def create_sqlite_db(csv_path: str, db_path: str):
    """
    Load a CSV file into an SQLite database.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_csv(csv_path)
    df.to_sql("your_table_name", conn, index=False, if_exists="replace")
    conn.close()
```

### Step 2: Run the Workflow

Execute the workflow by running the dq_profile.py script:
```bash
python dq_profiling.py
```
The process includes:

1-Fetching the database schema.
2-Generating profiling and data quality queries.
3-Executing queries and extracting results.
4-Formatting results into a Markdown report.


## Extending the Workflow

### Add Custom Tools:

-Integrate other data tools into CrewAI by creating custom tool classes like SQLiteSchemaTool and SQLiteQueryTool.
-Scale to Other Databases: Adapt the schema and query tools for other database systems (e.g., PostgreSQL, MySQL).
-Enhance Reporting: Include additional visualizations or summaries using libraries like matplotlib or seaborn.


## Contributing
Feel free to fork this repository and create a pull request with your improvements. Contributions are always welcome!

## License
This project is licensed under the MIT License. See the LICENSE file for details.

