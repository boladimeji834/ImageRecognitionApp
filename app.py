
from flask import Flask, request, render_template, url_for, flash
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input, decode_predictions
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './img'
app.secret_key = 'supersecretkey'

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Load VGG16 model with ImageNet weights
model = VGG16(weights='imagenet')

def prepare_image(img_path):
    """Preprocess image to match VGG16 input requirements."""
    img = load_img(img_path, target_size=(224, 224))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    return img

@app.route('/', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        # Check if an image file is uploaded
        if 'image' not in request.files or request.files['image'].filename == '':
            flash('No file selected or no file uploaded', 'danger')
            return render_template('index.html')

        file = request.files['image']

        # Save image to img folder
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(img_path)

        try:
            # Prepare image and make predictions
            img = prepare_image(img_path)
            yhat = model.predict(img)
            labels = decode_predictions(yhat)
            label = labels[0][0]

            classification = f"{label[1]} ({round(label[2] * 100, 2)}%)"
            logging.info(f"Prediction: {classification}")

            return render_template('index.html', classification=classification)

        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            flash('An error occurred during prediction. Please try again.', 'danger')
            return render_template('index.html')

    return render_template('index.html')

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])  # Ensure the img folder exists
    app.run(debug=True)


