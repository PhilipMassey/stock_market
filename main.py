import os

# Set the current working directory to the root of the project
os.chdir('./percent_app')

# Run the app
from app import app
if __name__ == '__main__':
    app.run_server(debug=True)
