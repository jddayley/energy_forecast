# Import necessary libraries
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Read the data and set low_memory=False
energy_df = pd.read_csv('forecast_new.csv', low_memory=False, comment='#')

# Print the column names to check the correct column name
print("Columns in the dataset:", energy_df.columns.tolist())

# Replace 'DateTime' with the correct column name from your CSV file
# For example, if the correct column name is 'Date_Time', replace 'DateTime' with 'Date_Time'
energy_df['ds'] = pd.to_datetime(energy_df['DateTime'])  # Modify 'DateTime' as needed

# Aggregate data by time to get total energy consumption per timestamp
energy_df = energy_df.groupby('ds').agg({'kWh': 'sum'}).reset_index()
energy_df.rename(columns={'kWh': 'y'}, inplace=True)

# Initialize the Prophet model with yearly seasonality
model = Prophet(yearly_seasonality=True)

# Fit the model with the dataset
model.fit(energy_df)

# Create a future dataframe
future = model.make_future_dataframe(periods=365, freq='D')

# Make predictions
forecast = model.predict(future)

# Plot the forecast
model.plot(forecast)
plt.title('Energy Consumption Forecast')
plt.show()

# Plot the forecast components
model.plot_components(forecast)
plt.show()

# Display the tail of the forecast dataframe
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
