# Import the database module so we can verify its functions exist
import database


# Test that the main database functions are available
def test_database_module_has_expected_functions():

    # Verify the function used to connect to MySQL exists
    assert hasattr(database, "get_connection")

    # Verify the function used to retrieve data exists
    assert hasattr(database, "fetch_data")

    # Verify the function used to execute INSERT, UPDATE, and DELETE queries exists
    assert hasattr(database, "run_query")

