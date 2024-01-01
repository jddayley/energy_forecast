from flask import Flask, request, jsonify, render_template
import pandas as pd
from prophet import Prophet
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO
application = Flask(__name__)

# Read and preprocess the forecast data
forecast_df = pd.read_csv('forecast_new.csv', comment='#')
forecast_df['ds'] = pd.to_datetime(forecast_df['DateTime'])
forecast_df = forecast_df.groupby('ds')['kWh'].sum().reset_index()
forecast_df.rename(columns={'kWh': 'y'}, inplace=True)

model = Prophet(daily_seasonality=True)
model.fit(forecast_df)

@application.route('/', methods=['GET', 'POST'])
def index():
    forecast_data = None
    graph_url = None
    if request.method == 'POST':
        input_date = request.form.get('date')
        time_range = request.form.get('range', 'day')

        if input_date:
            try:
                start_date = pd.to_datetime(input_date)
            except ValueError:
                start_date = pd.to_datetime('today')  # default or error handling

            forecast = get_forecast_for_period(model, start_date, time_range)
            forecast_data = forecast.to_html(classes="table table-striped table-bordered", border=0, index=False)

            file = request.files['file']
            actual_df = pd.DataFrame()
            if file and allowed_file(file.filename):
                actual_df = pd.read_csv(file.stream, comment='#')
                if 'DateTime' in actual_df.columns:
                    actual_df['ds'] = pd.to_datetime(actual_df['DateTime'])
                    actual_df['y'] = actual_df['kWh'] * 1000  # Convert to watts
                    actual_df = actual_df.groupby('ds').agg({'y': 'sum'}).reset_index()
                else:
                    print("DateTime column not found in uploaded file")

            if not actual_df.empty:
                graph_url = plot_forecast(forecast, actual_df, start_date)
            else:
                graph_url = plot_forecast(forecast, pd.DataFrame(), start_date)
        else:
            print("bad erro")
            # Handle case where date is not entered

    return render_template('index.html', forecast_data=forecast_data, graph_url=graph_url)
def plot_forecast(forecast, actual, date):
    plt.figure(figsize=(10, 4))
    plt.plot(forecast['ds'], forecast['yhat_watts'], label='Predicted')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'] * 1000, forecast['yhat_upper'] * 1000, alpha=0.3)
    
    if not actual.empty:
        plt.scatter(actual['ds'], actual['y'], color='red', label='Actual')
    
    plt.title(f'Hourly Energy Consumption Forecast vs Actual for {date}')
    plt.xlabel('Hour')
    plt.ylabel('Energy Consumption (Watts)')

    # Set x-axis to display AM/PM format
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=4))
    
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

@application.route('/api/upload_actuals', methods=['POST'])
def upload_actuals():
    file = request.files['file']
    input_date = request.form.get('date')
    time_range = request.form.get('range', 'day')

    if file:
        
        actual_df = pd.read_csv(file, comment='#')
        actual_df['ds'] = pd.to_datetime(actual_df['DateTime'])
        actual_df['y'] = actual_df['kWh'] * 1000  # Convert kWh to watts

        # Aggregate actual data by datetime
        actual_df = actual_df.groupby('ds').agg({'y': 'sum'}).reset_index()
        forecast = get_forecast_for_period(model, pd.to_datetime(input_date), time_range)
        graph_url = plot_forecast(forecast, actual_df, input_date)
        return jsonify({'graph': graph_url})

    return jsonify({'error': 'No file provided'}), 400
@application.route('/forecast_components', methods=['GET', 'POST'])
def forecast_components():
    if request.method == 'POST':
        # Assuming you have a form input where the user can enter a date
        input_date = request.form.get('date')
        time_range = request.form.get('range', 'day')  # Default to 'day' if not specified

        if input_date:
            try:
                start_date = pd.to_datetime(input_date)
            except ValueError:
                # Handle invalid date input
                start_date = pd.to_datetime('today')  # Default to today or handle the error as needed

            # Generate forecast using your existing logic
            forecast = get_forecast_for_period(model, start_date, time_range)
            future = model.make_future_dataframe(periods=30)

            # Forecast
            forecast = model.predict(future)
            #print(forecast.columns)
            # Generate the components plot
            graph_url = plot_forecast_components(model, forecast)

            return render_template('forecast_components.html', graph_url=graph_url)
        else:
            # Handle case where date is not entered or invalid
            # You may want to send an error message to the template or handle it differently
            pass

    return render_template('forecast_components.html')

def plot_forecast_components(model, forecast):
    fig = model.plot_components(forecast)
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return f"data:image/png;base64,{image_base64}"


def get_forecast_for_period(model, start_date, period):
    # Determine end_date based on period
    if period == 'day':
        end_date = start_date + pd.Timedelta(days=1)
    elif period == 'week':
        end_date = start_date + pd.Timedelta(weeks=1)
    elif period == 'month':
        end_date = start_date + pd.Timedelta(days=30)  # Approximation of a month
    else:
        raise ValueError(f"Invalid period: {period}")

    future_dates = pd.date_range(start=start_date, end=end_date, freq='H')
    future = pd.DataFrame(future_dates, columns=['ds'])
    forecast = model.predict(future)
    forecast['yhat_watts'] = forecast['yhat'] * 1000
    return forecast[['ds', 'yhat_watts', 'yhat_lower', 'yhat_upper', 'trend', 'trend_lower', 'trend_upper']]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv']

if __name__ == '__main__':
    application.run(debug=True)

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



    #return jsonify({'error': 'No file provided'}), 400
def api_forecast():
    data = request.get_json()
    input_date = data.get('date')
    time_range = data.get('range', 'day')

    try:
        start_date = pd.to_datetime(input_date)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format'}), 400

    forecast = get_forecast_for_period(model, start_date, time_range)

    actual_df = pd.DataFrame(data.get('actuals', []))
    if not actual_df.empty:
        actual_df['ds'] = pd.to_datetime(actual_df['DateTime'])
        actual_df['y'] = actual_df['kWh'] * 1000
        actual_df = actual_df.groupby('ds').agg({'y': 'sum'}).reset_index()

    graph_url = plot_forecast(forecast, actual_df, start_date)
    return jsonify({'forecast': forecast.to_dict(orient='records'), 'graph': graph_url})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv']

if __name__ == '__main__':
    application.run(debug=True)
