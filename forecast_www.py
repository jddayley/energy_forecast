from flask import Flask, request, render_template
import pandas as pd
from prophet import Prophet
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)

# Read and preprocess the forecast data
forecast_df = pd.read_csv('forecast_new.csv', comment='#')
forecast_df['ds'] = pd.to_datetime(forecast_df['DateTime'])
forecast_df = forecast_df.groupby('ds')['kWh'].sum().reset_index()
forecast_df.rename(columns={'kWh': 'y'}, inplace=True)

# Initialize and train the Prophet model
model = Prophet(daily_seasonality=True)
model.fit(forecast_df)

@app.route('/', methods=['GET', 'POST'])
def index():
    forecast_data = None
    graph_url = None
    if request.method == 'POST':
        input_date = request.form['date']
        time_range = request.form['range']
        file = request.files['file']

        actual_df = pd.DataFrame()
        if file and allowed_file(file.filename):
            actual_df = pd.read_csv(file.stream)
            actual_df['ds'] = pd.to_datetime(actual_df['DateTime'])
            actual_df['y'] = actual_df['kWh'] * 1000  # Convert to watts if needed

        forecast = get_forecast_for_period(model, input_date, time_range)
        forecast_data = forecast.to_html()

        if not actual_df.empty:
            graph_url = plot_forecast(forecast, actual_df, input_date)
        else:
            graph_url = plot_forecast(forecast, pd.DataFrame(), input_date)

    return render_template('index.html', forecast_data=forecast_data, graph_url=graph_url)

def get_forecast_for_period(model, start_date, period):
    start_date = pd.to_datetime(start_date)
    if period == 'day':
        end_date = start_date + pd.Timedelta(days=1)
    elif period == 'week':
        end_date = start_date + pd.Timedelta(weeks=1)
    elif period == 'month':
        end_date = start_date + pd.Timedelta(days=30)  # Approximation of a month

    future_dates = pd.date_range(start=start_date, end=end_date, freq='H')
    future = pd.DataFrame(future_dates, columns=['ds'])
    forecast = model.predict(future)
    forecast['yhat_watts'] = forecast['yhat'] * 1000
    return forecast[['ds', 'yhat_watts', 'yhat_lower', 'yhat_upper']]

def plot_forecast(forecast, actual, date):
    plt.figure(figsize=(10, 4))
    plt.plot(forecast['ds'], forecast['yhat_watts'], label='Predicted')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'] * 1000, forecast['yhat_upper'] * 1000, alpha=0.3)
    if not actual.empty:
        plt.scatter(actual['ds'], actual['y'], color='red', label='Actual')
    plt.title(f'Hourly Energy Consumption Forecast vs Actual for {date}')
    plt.xlabel('Hour')
    plt.ylabel('Energy Consumption (Watts)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()
    return f"data:image/png;base64,{image_base64}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv']

if __name__ == '__main__':
    app.run(debug=True)
