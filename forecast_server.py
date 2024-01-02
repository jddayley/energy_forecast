from flask import Flask, request, jsonify, render_template
from prophet import Prophet
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO
application = Flask(__name__)
application.secret_key = 'your_secret_key_here'

import pandas as pd
from flask import flash, redirect
# Load the CSV file
file_path = 'data/forecast_new.csv'  # Replace with your CSV file path
forecast_df = pd.read_csv(file_path, comment='#')

# Convert 'DateTime' to datetime objects
forecast_df['ds'] = pd.to_datetime(forecast_df['DateTime'])

# Aggregate 'kWh' values by 'ds'
aggregated_kWh = forecast_df.groupby('ds')['kWh'].sum().rename('y').reset_index()

# Check if the columns exist before attempting to drop them
#columns_to_drop = ['DateTime', 'kWh']
#columns_to_drop = ['DateTime']
#columns_to_drop = [col for col in columns_to_drop if col in forecast_df.columns]

# Drop the columns and merge with aggregated values
forecast_df = forecast_df.drop_duplicates().merge(aggregated_kWh, on='ds')

# Now, forecast_df contains 'ds', 'y', and other columns like 'Device ID' and 'Name'

# # Read and preprocess the forecast data
# forecast_df = pd.read_csv('forecast_new.csv', comment='#')
# forecast_df['ds'] = pd.to_datetime(forecast_df['DateTime'])
# forecast_df = forecast_df.groupby('ds')['kWh'].sum().reset_index()
# forecast_df.rename(columns={'kWh': 'y'}, inplace=True)

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
            print("No Date provided error - Index.html")
            # Handle case where date is not entered

    return render_template('index.html', forecast_data=forecast_data, graph_url=graph_url)
# Dummy functions for demonstration


def get_top_10_devices():
    # Aggregate total watts used by each device
    total_watts_by_device = forecast_df.groupby('Device ID')['y'].sum()

    # Sort by total watts in descending order and get top 10 devices
    top_10_devices = total_watts_by_device.sort_values(ascending=False).head(10)

    #print(top_10_devices)
    return top_10_devices

from prophet import Prophet

@application.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global forecast_df, model  # Declare global variables

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):

            if forecast_df is not None:
                del forecast_df
            forecast_df = pd.read_csv(file, low_memory=False, comment='#')

            if 'DateTime' not in forecast_df.columns:
                flash('Uploaded file must contain a DateTime column')
                return redirect(request.url)

            forecast_df['ds'] = pd.to_datetime(forecast_df['DateTime'])
            aggregated_kWh = forecast_df.groupby('ds')['kWh'].sum().rename('y').reset_index()
            forecast_df = forecast_df.drop(['DateTime'], axis=1).drop_duplicates().merge(aggregated_kWh, on='ds')

            # Instantiate a new Prophet model
            if model is not None:
                del model
            model = Prophet(daily_seasonality=True)
            model.fit(forecast_df)

            flash('File successfully uploaded and processed')
            return redirect('/')

    return render_template('upload.html')


@application.route('/device_forecast', methods=['GET', 'POST'])
def device_forecast():
    forecast_data = None
    graph_url = None
    #print("Debug")
    #print(forecast_df.columns)
    top_10_devices = get_top_10_devices()
    
    #print(top_10_devices)
    unique_devices = forecast_df[['Device ID', 'Name']].drop_duplicates()
    unique_devices_filtered = unique_devices[unique_devices['Device ID'].isin(top_10_devices)]
    unique_devices_dict = unique_devices_filtered.to_dict(orient='records')
    #unique_devices_filtered = unique_devices[unique_devices['Device ID'].isin(top_10_devices)]

    #print(unique_devices)
    print(forecast_df.columns)
    if request.method == 'POST':
        print("Form data received:")
        for key in request.form:
            print(f"{key}: {request.form[key]}")
        device_id = request.form.get('device_id')
        print("Device: " + device_id)
        time_range = request.form.get('range', 'day')

        # Filter data for the selected device
        forecast_df_filtered = forecast_df[forecast_df['Device ID'] == device_id]
        
        if forecast_df_filtered.empty:
            print("ERROR:  No paramater passed: " + device_id)
            return render_template('device_forecast.html', unique_devices=unique_devices_dict, error="Device not found")

        # Prepare the model and data for forecasting
        forecast_df_filtered = forecast_df_filtered.groupby('ds')['kWh'].sum().reset_index()
        forecast_df_filtered.rename(columns={'kWh': 'y'}, inplace=True)

        model = Prophet(daily_seasonality=True)
        model.fit(forecast_df_filtered)
        
        # Generate forecast for the specified period
        try:
            start_date = pd.to_datetime('today')  # You can modify this as needed
            forecast = get_forecast_for_period(model, start_date, time_range)
            forecast_data = forecast.to_html(classes="table table-striped table-bordered", border=0, index=False)
            
            # Optionally, you can include actual data comparison here
            # ...

            graph_url = plot_forecast(forecast, pd.DataFrame(), start_date)

        except Exception as e:
            # Handle exceptions
            return render_template('device_forecast.html', error=str(e))

    return render_template('device_forecast.html', forecast_data=forecast_data, graph_url=graph_url, unique_devices=unique_devices,top_10_devices=top_10_devices)


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