# AI Instructions for the Stock Market Project

These are specific guidelines and information for the AI (Antigravity) when working on this project.

## Database Management
- **Connection Singleton**: The project uses a Singleton pattern for MongoDB connections (`client = MongoClient()`). Avoid creating multiple separate instances of MongoClient to prevent connection leaks and timeouts. Always use the shared connection helper if it exists.
- **Service requirement**: MongoDB needs to be running locally for most data operations and Dash apps to function.

## Code Standards
- **Logging vs. Printing**: Minimize the use of `print()` statements in data processing functions so production logs remain clean.
- **Naming Conventions**: Keep file names specific and free of generic or redundant prefixes (e.g., avoid `dash_fidelity_` where not needed).

## User Interaction
- **Testing Before Displaying Changes**: Whenever possible, run Python files locally to ensure data logic returns what is expected. 
- **Verifying Web Output**: For Dash app changes (`dash_prj` or `percent_app`), consider that the apps visualize data stored in MongoDB. Be mindful of data formats, especially percentage value changes or volume changes.

## Workflows Available
You have slash commands configured under `.agent/workflows/`:
- `/start-mongodb` - To start the MongoDB server in the background.
- `/run-percent-app` - To trigger the `percent_app` module in the background.
