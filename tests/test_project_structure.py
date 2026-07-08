# Import Path so we can check if important project files exist
from pathlib import Path


# Test that the essential project files are present
def test_required_project_files_exist():

    # Verify the main Streamlit application exists
    assert Path("app.py").exists()

    # Verify the database helper module exists
    assert Path("database.py").exists()

    # Verify the dependency file exists
    assert Path("requirements.txt").exists()