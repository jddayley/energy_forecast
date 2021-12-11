from prophet import Prophet
import numpy as np
import pandas as pd

#read the files
energy_df = pd.read_csv('stats-pw.csv')
#create a backup of the org
energy_df.set_index('ds').y.plot().get_figure()
energy_df['y_orig'] = energy_df['y'] # to save a copy of the original data..you'll see why shortly. 
# log-transform y

#model = Prophet() #instantiate Prophet
model = Prophet( yearly_seasonality=True )
#model = Prophet( )
model.fit(energy_df); #fit the model with your dataframe

#Python
future = model.make_future_dataframe(periods=365)
future.tail()

# Python
forecast = model.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

# Python
# Python
fig1 = model.plot(forecast)
fig2 = model.plot_components(forecast)