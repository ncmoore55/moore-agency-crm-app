# Import the MySQL connector library
import mysql.connector

# Import pandas for reading SQL queries into DataFrames
import pandas as pd

# Import os so we can read environment variables
import os

# Import dotenv so Python can load variables from the .env file
from dotenv import load_dotenv

# Ignore the SQLAlchemy warning from pandas
import warnings
warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy"
)

# Load the environment variables from the .env file
load_dotenv()

def get_connection():

    return mysql.connector.connect(

        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")

    )

# Function to retrieve data from the database
def fetch_data(query, params=None):

    # Create a connection to the database
    conn = get_connection()

    # Execute the SQL query and store the results in a DataFrame
    # params lets callers pass values safely instead of splicing them into the query string
    df = pd.read_sql(query, conn, params=params)

    # Close the database connection
    conn.close()

    # Return the data back to app.py
    return df

# Function to execute INSERT, UPDATE, and DELETE queries
def run_query(query, values=None):

    # Connect to the database 
    conn = get_connection()

    # Create a cursor to execute SQL commands
    cursor = conn.cursor()

    # Execute the SQL query
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)

    # Save the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()