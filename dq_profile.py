import os
import pandas as pd
import sqlite3
import json
from crewai import Agent, Task, Crew, Process



class SQLiteSchemaTool:
    def __init__(self):
        self.name = "SQLiteSchemaTool"
        self.description = "Fetches table names and column names from an SQLite database."
        self.func = self.fetch_schema

    def fetch_schema(self, db_path: str) -> str:
        """
        Fetches the schema (tables and columns) from the SQLite database.
        """
        db_path = "database.db"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Fetch table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

            schema = {}
            for table in tables:
                # Fetch column names for each table
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]
                schema[table] = columns

            conn.close()
            return json.dumps(schema, indent=4)
        except Exception as e:
            return f"Error fetching schema: {str(e)}"


# Define a custom tool class that meets CrewAI requirements
class SQLiteQueryTool:
    def __init__(self):
        self.name = "SQLiteQueryTool"
        self.description = (
            "Executes SQL queries on a SQLite database. Provide `db_path` and `query`."
        )
        self.func = self.execute_query

    def execute_query(self, db_path: str, query: str) -> str:
        """
        Execute an SQL query on the provided SQLite database.
        """
        db_path = "database.db"
        print(f"Running query: {query}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            conn.close()
            result = [dict(zip(columns, row)) for row in rows]
            return json.dumps(result, indent=4)
        except Exception as e:
            return f"Error executing query: {str(e)}"


# Environment Configuration
os.environ["OPENAI_API_KEY"] = ""


schema_tool_instance = SQLiteSchemaTool()
# Instantiate the SQLite query tool
sqlite_tool_instance = SQLiteQueryTool()

# Agents
profiling_agent = Agent(
    role="Data Profiling Agent",
    goal="Generate SQL queries for profiling and data quality.",
    model="gpt4",
    verbose=True,    # Optional: For debugging purposes
    memory=True,
    tools=[schema_tool_instance],  # Add schema tool here
    backstory="An expert in crafting insightful SQL queries for data analysis.",
)

execution_agent = Agent(
    role="SQL Query Executor",
    goal="Execute SQL queries and return the results.",
    backstory="Specializes in running SQL queries and fetching results.",
    model="gpt4",
    verbose=True,    # Optional: For debugging purposes
    memory=True,
    tools=[sqlite_tool_instance],  # Use the tool instance
)

presentation_agent = Agent(
    role="Markdown Presenter",
    goal="Present data in a well-structured Markdown format.",
    model="gpt4",
    verbose=True,    # Optional: For debugging purposes
    memory=True,
    backstory="An experienced Markdown formatter, skilled in converting raw data into beautifully formatted reports.",
)

# Tasks
profiling_task = Task(
    description=(
        "First, use the `SQLiteSchemaTool` to fetch the schema (table names and column names) "
        "from the database. Then generate SQL queries to profile the data based on the schema. "
        "Ensure the queries are relevant and use the actual table and column names."
        "Then generate SQL queries to profile the data. Ensure the queries:\n"
        "1. Count the total number of records for each column.\n"
        "2. Summarize categorical columns (e.g., counts by category, distinct values, unique values by % , min length, max length, mean length) .\n"
        "3. Calculate basic statistics (e.g., mean, median, min, max) for numerical columns.\n"
        "Analyze the provided database to identify potential data quality issues. "
        "Focus on finding:\n"
        "1. Missing values (NULLs) in each column.\n"
        "2. Duplicate records.\n"
        "3. Outliers in numerical columns (e.g., values beyond 1.5 times the IQR).\n"
        "4. Inconsistent or invalid values (e.g., mismatched data types, incorrect categories).\n"
        "5. Violations of referential integrity if foreign key relationships exist.\n\n"
        "Use the `SQLiteSchemaTool` to fetch the schema and ensure all queries are based on actual table and column names. "
        "Provide SQL queries that specifically address these data quality checks."
        
    ),
    expected_output="A list of SQL queries for profiling and validation",
    agent=profiling_agent,
    output_file="profile.yaml",
    allow_failures=True,
)

data_quality_task = Task(
    description=(
        "Analyze the provided database to identify potential data quality issues. "
        "Focus on finding:\n"
        "1. Missing values (NULLs) in each column.\n"
        "2. Duplicate records.\n"
        "3. Outliers in numerical columns (e.g., values beyond 1.5 times the IQR).\n"
        "4. Inconsistent or invalid values (e.g., mismatched data types, incorrect categories).\n"
        "5. Violations of referential integrity if foreign key relationships exist.\n\n"
        "Use the `SQLiteSchemaTool` to fetch the schema and ensure all queries are based on actual table and column names. "
        "Provide SQL queries that specifically address these data quality checks."
    ),
    expected_output="A list of SQL queries for validation",
    agent=profiling_agent,
    output_file="dq.yaml",
    allow_failures=True,
)

execution_task = Task(
    description=(        
        "Use the `SQLiteQueryTool` to execute SQL queries on the database from profiling_task and data_quality_task "
        "Provide the `db_path` and `query` arguments. For example, use the query: "
        "'SELECT COUNT(*) AS total_records FROM hr_data;'."
),
    expected_output="Query results in a YAML file.",
    agent=execution_agent,
    output_file="results.yaml",
    allow_failures=True,
)

presentation_task = Task(
    description="Format SQL query results into a Markdown report.",
    expected_output=(
        "A Markdown file containing:\n"
        "1. Query Results as tables.\n"
        "2. A summary of findings from both the profiling tasks and data quality tasks"
    ),
    agent=presentation_agent,
    output_file="report.md",
    allow_failures=True,
)

# Crew
crew = Crew(
    agents=[profiling_agent, execution_agent, presentation_agent],
    tasks=[profiling_task, execution_task, presentation_task],
    process=Process.sequential,
)

# Helper Function: Create SQLite Database
def create_sqlite_db(csv_path: str, db_path: str):
    """
    Load a CSV file into an SQLite database.

    Args:
        csv_path (str): Path to the CSV file.
        db_path (str): Path to the SQLite database.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_csv(csv_path)
    df.to_sql("hr_data", conn, index=False, if_exists="replace")
    conn.close()

# Main Script
if __name__ == "__main__":
    # Prepare the data
    csv_file = "dataset.csv"
    sqlite_db = "database.db"
    
    # Uncomment this line if you need to create the SQLite database from the CSV
    #create_sqlite_db(csv_file, sqlite_db)

    # Execute the crew
    inputs = {"db_path": sqlite_db}
    results = crew.kickoff(inputs)
    # Extract the result in a JSON-serializable format
    if hasattr(results, "to_dict"):
        # If a `.to_dict()` method exists
        output = results.to_dict()
    else:
        # Otherwise, handle manually (example assumes .data or similar attribute exists)
        output = {
            "tasks": [task_result for task_result in results.tasks],
            "summary": results.summary if hasattr(results, "summary") else None,
        }

    # Print the serialized output
    print(json.dumps(output, indent=4))
