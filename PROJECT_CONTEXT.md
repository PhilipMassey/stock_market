# Project Context: Stock Market

## Overview
This is a Python-based project for analyzing and visualizing stock market data, tracking portfolio performance, and examining sector/industry value changes.

## Tech Stack
- **Language**: Python
- **Database**: MongoDB (used for storing market data, sector/industry info)
- **Frontend/Visualization**: Dash / Plotly (`dash_prj`, `percent_app`)
- **Data Processing**: Pandas

## Key Components
- **Market Data Analysis**: Extracting and transforming data related to sectors, industries, and specific symbols (e.g., XLK, PLTM).
- **Portfolio Tracking**: Analyzing portfolio value changes, quantity changes, and total sector values.
- **Dash Applications**: Interactive web applications located in `dash_prj` and `percent_app` directories.
- **Data Ingestion**: Using scripts to pull data (e.g., MongoDB connections, APIs, and web scraping like Google News).

## Architectural Guidelines
- **Database Connections**: Use the Singleton pattern for MongoDB connections to prevent connection leaks and timeouts.
- **Logs**: Keep production logs clean by minimizing `print()` statements.
- **File Naming**: Maintain clean file names without unnecessary prefixes.
