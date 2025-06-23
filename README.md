# European Energy Modeling & ETL Platform

This repository contains a modular ETL and analytics platform for modeling European LNG consumption using weather, economic, and financial data. It includes a data pipeline orchestrated with Prefect, a Flask-based UI, and custom integrations with multiple data providers.

## 📦 Project Structure

```
.
├── dwh/       # Data warehouse orchestration (Prefect flows)
├── app/       # Flask web application for visualizing and interacting with the data
```

## ⚙️ Key Features

- **Prefect-based ETL orchestration** in `dwh/` for repeatable and monitored data workflows.
- **Flask web app** in `app/` for presenting processed data via a browser-based UI.
- **ETL integrations** for:
  - 🇪🇺 **Eurostat**: Country-level LNG consumption data
  - ☁️ **Bright Sky & Yr.no**: City-level weather data for HDD (heating degree day) modeling
  - 📈 **Mboum**: Financial and stock data
  - 📊 **SEC Edgar**: Company filings and fundamental data (facts)
  - 🗃️ **PostgreSQL**: Database ingestion/export
  - 💬 **Discord**: Automated bot for data updates and alerts

## 🔍 Energy Modeling

The core model estimates **European LNG consumption** using:

- **Heating Degree Days (HDD)** derived from city-level temperature data
- **Country-level energy consumption trends** from Eurostat
- **Weather-driven demand estimation** using brightsky and yr.no

## 🛠️ Installation & Usage

> **Note:** Setup instructions, dependencies, and Prefect configuration will be added here once deployment is finalized.

## 📈 Example Use Cases

- Monitor and forecast LNG demand in Europe based on changing weather patterns
- Analyze stock seaonality and SEC data
- Trigger Discord notifications for seasonality requests and daily weather updates

