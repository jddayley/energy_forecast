from time import sleep
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from datetime import timedelta

import pandas as pd

# Load the data from a CSV file
df = pd.read_csv("/Users/ddayley/Desktop/Forecast/forecast.csv")
#df = df.tail(-1)

# Convert the 'DateTime' column to a datetime type
# df['DateTime'] = pd.to_datetime(df['DateTime'])
# df.set_index('DateTime', inplace=True)
#import pandas as pd


# Sample data - replace this with your data reading method
# 
#df = pd.DataFrame(data)

# Rename columns for Prophet compatibility
df = df.rename(columns={'DateTime': 'ds', 'kWh': 'y'})
head = df.head()
print (head)
# Train the model
model = Prophet(yearly_seasonality=True)
model.fit(df)

# Make a future dataframe for next 30 days (adjust the period as needed)
future = model.make_future_dataframe(periods=30)

# Forecast
forecast = model.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

# Plot the results
fig = model.plot(forecast)
sleep(1)
# If you want to make forecasts per 'type', you'd segment the data by type and repeat the above steps for each segment.

# Uncomment to use:
# types = df['type'].unique()
# for t in types:
#     segment_df = df[df['type'] == t]
#     model = Prophet()
#     model.fit(segment_df)
#     future = model.make_future_dataframe(periods=30)
#     forecast = model.predict(future)
#     fig = model.plot(forecast)

# Finally, if you want to plot the components (trend, yearly seasonality, etc.), you can use:
# fig2 = model.plot_components(forecast)

