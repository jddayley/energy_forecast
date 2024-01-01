from forecast_server import application

if __name__ == "__main__":
 application.run(debug=True, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
