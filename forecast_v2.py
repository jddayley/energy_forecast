# Import necessary libraries
from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt
from math import log, exp

# Read the data
energy_df = pd.read_csv('forecast.csv')

# Format the 'DateTime' column and select relevant columns for forecasting
energy_df['ds'] = pd.to_datetime(energy_df['DateTime'])
energy_df['y'] = energy_df['kWh']  # Target variable for forecasting

# Aggregate data by time to get total energy consumption per timestamp
# This step sums up the kWh usage for all devices for each timestamp
energy_df = energy_df.groupby('ds').agg({'y': 'sum'}).reset_index()

# Create a copy of the original data for later comparison
energy_df['y_orig'] = energy_df['y']

# Apply log transformation to stabilize variance (optional)
# Uncomment the following line if you decide to use log transformation
# energy_df['y'] = energy_df['y'].apply(lambda x: log(x) if x > 0 else 0)

# Initialize the Prophet model with yearly seasonality
model = Prophet(yearly_seasonality=True)

# Fit the model with the dataset
model.fit(energy_df)

# Create a future dataframe for the next 365 days
future = model.make_future_dataframe(periods=365)

# Make predictions
forecast = model.predict(future)

# Plot the forecast
fig1 = model.plot(forecast)
plt.title('Energy Consumption Forecast')
plt.show()

# Plot the forecast components
fig2 = model.plot_components(forecast)
plt.show()

# Optional: Revert log transformation for interpretability
# Uncomment the following lines if you used log transformation
# forecast['yhat_exp'] = forecast['yhat'].apply(exp)
# forecast['yhat_lower_exp'] = forecast['yhat_lower'].apply(exp)
# forecast['yhat_upper_exp'] = forecast['yhat_upper'].apply(exp)

# Display the tail of the forecast dataframe
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
