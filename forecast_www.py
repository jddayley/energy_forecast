from flask import Flask, request, render_template
import pandas as pd
from prophet import Prophet

app = Flask(__name__)

# Read and preprocess the data (this should be done outside of your route to load it only once)
energy_df = pd.read_csv('forecast_new.csv', comment='#')
energy_df['ds'] = pd.to_datetime(energy_df['DateTime'])
energy_df = energy_df.groupby('ds')['kWh'].sum().reset_index()
energy_df.rename(columns={'kWh': 'y'}, inplace=True)

# Initialize and train the Prophet model
model = Prophet(daily_seasonality=True)
model.fit(energy_df)

@app.route('/', methods=['GET', 'POST'])
def index():
    forecast_data = None
    if request.method == 'POST':
        input_date = request.form['date']
        forecast_data = get_hourly_forecast_for_date(model, input_date)
    return render_template('index.html', forecast_data=forecast_data)

def get_hourly_forecast_for_date(model, date):
    start_date = pd.to_datetime(date)
    end_date = start_date + pd.Timedelta(days=1)
    future_dates = pd.date_range(start=start_date, end=end_date, freq='H')
    future = pd.DataFrame(future_dates, columns=['ds'])
    forecast = model.predict(future)
    forecast['yhat_watts'] = forecast['yhat'] * 1000
    forecast['yhat_lower_watts'] = forecast['yhat_lower'] * 1000
    forecast['yhat_upper_watts'] = forecast['yhat_upper'] * 1000
    return forecast[['ds', 'yhat_watts', 'yhat_lower_watts', 'yhat_upper_watts']].to_html()

if __name__ == '__main__':
    app.run(debug=True)
