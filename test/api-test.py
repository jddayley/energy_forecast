import requests
import base64
from io import BytesIO
from PIL import Image
import re
import base64
import json

url = 'http://127.0.0.1:5000/api/upload_actuals'
files = {'file': open('data/actual_week.csv', 'rb')}
data = {'date': '2023-12-25', 'range': 'month'}

response = requests.post(url, files=files, data=data)
if response.status_code == 200:
    try:
        #print(response.json())
        # Sample base64 encoded image (replace with your own)
                # Split the base64 data to get the actual image data
        image_data = re.search(r'base64,(.*)', response.json()['graph']).group(1)
        #image_data = base64_data.split(',')[1]

        # Decode base64 and create an Image object
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))

        # Save the image as a PNG file
        image.save("img/output_image.png", "PNG")
    except json.JSONDecodeError:
        print("Response is not in JSON format.")
else:
    print("Error:", response.status_code, response.text)


