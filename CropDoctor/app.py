from flask import Flask, render_template, request
import requests
import os
import base64
from google import genai

app = Flask(__name__)

# 📁 Upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 🔑 API Keys (replace with your own)
PLANT_API_KEY = "MyS7p7BqcZ3VhG4dTlVswATOVAxIS1YarpFYraCNVgZyDpYubk"
GEMINI_API_KEY = "AIzaSyAav8iAZcWzBwGYUSVL5Rb52dwM5Bg4GcE"

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# 🌿 Get plant name
def get_plant_name(image_path):
    url = "https://plant.id/api/v3/identification"

    headers = {
        "Api-Key": PLANT_API_KEY,
        "Content-Type": "application/json"
    }

    with open(image_path, "rb") as img:
        img_base64 = base64.b64encode(img.read()).decode()

    data = {"images": [img_base64]}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    try:
        best = result["result"]["classification"]["suggestions"][0]
        return best["name"]
    except:
        return None

# 🧠 Gemini AI (NEW VERSION)
def get_disease_info(plant_name):
    prompt = f"""
    A farmer uploaded a plant leaf.

    Plant: {plant_name}

    Give:
    Disease:
    Cure:
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text

    except:
        return """Disease: Leaf Infection
Cure: Apply neem oil spray and remove infected leaves"""

# 🌐 Main route
@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    image_path = None

    if request.method == 'POST':
        file = request.files['image']

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            plant = get_plant_name(filepath)

            if plant:
                ai_result = get_disease_info(plant)
                result = f"🌿 Plant: {plant}\n{ai_result}"
            else:
                result = "❌ Could not detect plant"

            image_path = filepath

    return render_template('index.html', result=result, image_path=image_path)

# 🚀 Run
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)