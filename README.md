# Energy Consumption Forecasting with Prophet
<div align="center">
<img src="img/Electric_Forecast.png" width="25%" >
</div>
This repository contains the code and datasets used for forecasting energy consumption based on data from Sense.com using Facebook's Prophet time series forecasting tool. The project focuses on predicting future energy consumption based on historical data gathered from Sense.com's smart energy monitoring devices.

## Project Overview

The main goal of this project is to provide accurate forecasts of energy consumption using data from Sense.com. By analyzing historical consumption data from various devices monitored by Sense.com, this project aims to predict future energy usage, which can be critical for efficient energy management, cost reduction, and understanding consumption patterns. The forecasting model is built using the Prophet library, designed to handle time series data with daily or sub-daily observations.

<div align="center">
<img src="img/screenshot.png" width="75%" >
  <img src="img/screenshot_2.png" width="75%" >
</div>

# Energy Consumption Forecasting Application

## Introduction

This Flask application provides a platform for energy consumption forecasting using Facebook's Prophet time series forecasting tool. The application allows users to upload historical energy consumption data, view forecasts for energy usage, and analyze the performance of predictions against actual data.

## Features

- **Data Upload**: Users can upload their own dataset in CSV format for forecasting.
- **Forecast Visualization**: View energy consumption forecasts over a specified time range.
- **Comparison with Actual Data**: Users can upload actual consumption data to compare against forecasts.
- **Top 10 Device Analysis**: Analyze energy consumption patterns for the top 10 most energy-intensive devices.

## Installation

Before running the application, ensure that you have Python and all required libraries installed. The main dependencies are Flask and Prophet.

1. **Clone the Repository**

   ```bash
   git clone https://your-repository-url.git
   cd your-repository-folder ```
 ```bash
 python -m venv venv ```
 source venv/bin/activate  # On Windows use `venv\Scripts\activate
 pip install -r requirements.txt
```
## Usage
To use the application:
 - Navigate to `http://localhost:5000`.

To use the API:
- Endpoint: `/api/upload_actuals`
- Method: POST
- Data: File upload with actuals data

# Energy Consumption Forecasting Application

## Introduction

This Flask application provides a platform for energy consumption forecasting using Facebook's Prophet time series forecasting tool. The application allows users to upload historical energy consumption data, view forecasts for energy usage, and analyze the performance of predictions against actual data.

## Features

- **Data Upload**: Users can upload their own dataset in CSV format for forecasting.
- **Forecast Visualization**: View energy consumption forecasts over a specified time range.
- **Comparison with Actual Data**: Users can upload actual consumption data to compare against forecasts.
- **Top 10 Device Analysis**: Analyze energy consumption patterns for the top 10 most energy-intensive devices.

## Installation

Before running the application, ensure that you have Python and all required libraries installed. The main dependencies are Flask and Prophet.

1. **Clone the Repository**

   ```bash
   git clone https://your-repository-url.git
   cd your-repository-folder
   ```
**Set Up a Virtual Environment (Optional but recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
**Install Dependencies**
```bash
pip install -r requirements.txt
```

## Usage

Starting the Flask Server
Run the Flask application with:

```bash
Copy code
python forecast_server.py
```

The application will start running on http://localhost:5000.
**Uploading Data**
Navigate to the upload page at http://localhost:5000/upload.
Choose your CSV file and click 'Upload'
**Viewing Forecasts**
Select a device and time range on the homepage.
Submit the form to view the energy consumption forecast.
**Comparing with Actual Data**
Use the 'Upload Actuals' API endpoint to upload actual consumption data.
The forecast graph will update to show a comparison between predicted and actual data.

## API Example
Using `curl`:
```bash
curl -X POST http://localhost:5000/api/upload_actuals \
-F "file=@/path/to/your/actuals.csv" \
-F "date=2023-01-01" \
-F "range=day"
```



Authors

Don Dayley - Initial work - jddayley


License

This project is licensed under the MIT License - see the LICENSE.md file for details.

Acknowledgments
