from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from pymongo import MongoClient

app = FastAPI()

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the TensorFlow model (ensure the model file path is correct)
model = tf.keras.models.load_model("trained_plant_disease_model.keras")

# Class names for prediction
class_names = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
    'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot',
    'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
    'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot',
    'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")  # Replace with your MongoDB URI
db = client["plant_disease_db"]  # Replace with your database name
collection = db["disease_info"]  # Replace with your collection name

@app.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    try:
        # Read the image file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB") #to ensures the images should be in the RGB format

        # Preprocess the image
        image = image.resize((128, 128))  # Resize to match model's expected input size
        input_arr = tf.keras.preprocessing.image.img_to_array(image)  # Convert to array
        input_arr = np.array([input_arr])  # Add batch dimension

        # Make prediction
        predictions = model.predict(input_arr)
        predicted_class = np.argmax(predictions)
        disease_name = class_names[predicted_class]

        # Fetch disease details from MongoDB
        disease_details = collection.find_one({"name": disease_name}, {"_id": 0})  # Exclude `_id` field

        if disease_details:
            return {
                "success": True,
                "predicted_disease": disease_name,
                "details": disease_details
            }
        else:
            return {
                "success": True,
                "predicted_disease": disease_name,
                "details": "No additional information found for this disease."
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

# New API to fetch pesticides for a specific disease
@app.get("/pesticides/{disease_name}")
def get_pesticides(disease_name: str):  #this is annotation in  the pytho that means that disease_name  should be in  the string format 
    try:
        # Fetch pesticide information from the "pesticides" collection
        pesticide_details = db["pesticides"].find_one({"disease_name": disease_name}, {"_id": 0})  # Exclude `_id`

        if pesticide_details:
            return {
                "success": True,
                "disease_name": disease_name,
                "chemicalControl": pesticide_details.get("chemicalControl", {}),
                "biologicalControl": pesticide_details.get("biologicalControl", {}),
                "recommendedPesticides": pesticide_details.get("recommendedPesticides", [])
            }
        else:
            return {
                "success": False,
                "message": f"No pesticide information found for disease '{disease_name}'."
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Root route
@app.get("/")
def root():
    return {"message": "Plant Disease Recognition API with MongoDB is running!"}
