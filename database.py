# Import the MySQL connector library so Python can communicate with MySQL
import mysql.connector

import pandas as pd

# Function to create and return a connection to our MySQL database
def get_connection():

    # Connect to the agency_crm database using our login credentials
    return mysql.connector.connect(

        # The database server is running on this computer
        host="localhost",

        # MySQL username
        user="root",

        # MySQL password
        password="Lacrosse12!",

        # The database (schema) we want to connect to
        database="agency_crm"
    )

# Function to retrieve data from the database
def fetch_data(query):

    # Create a connection to the database 
    conn = get_connection()

    # Execute the SQL query and store the results in a DataFrame
    df = pd.read_sql(query, conn)

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