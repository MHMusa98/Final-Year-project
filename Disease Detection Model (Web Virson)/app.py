# Import necessary libraries and modules
import os
import uuid
import flask
import urllib
from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request, send_file
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Initialize Flask application
app = Flask(__name__)

# Define the base directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load pre-trained model
model = load_model(os.path.join(BASE_DIR, 'model.hdf5'))

# Set of allowed file extensions
ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'jfif'])

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXT

# List of classes for predictions
classes = ['Bacterial leaf blight', 'Brown_Spot', 'Healthy', 'Hispa', 'Leaf smut', 'Leaf_Blast']

# Function to predict class and probabilities for an image
def predict(filename, model):
    img = load_img(filename, target_size=(112, 112))
    img = img_to_array(img)
    img = img.reshape(1, 112, 112, 3)
    img = img.astype('float32')
    img = img / 255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(6):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]
    
    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i] * 100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result

# Route for homepage
@app.route('/')
def home():
    return render_template("index.html")

# Route for processing image upload and providing prediction results
@app.route('/success', methods=['GET', 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try:
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename + ".jpg"
                img_path = os.path.join(target_img, filename)
                output = open(img_path, "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                }

            except Exception as e:
                print(str(e))
                error = 'This image from this site is not accessible or inappropriate input'

            if(len(error) == 0):
                return  render_template('success.html', img=img, predictions=predictions)
            else:
                return render_template('index.html', error=error) 

            
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                img = file.filename

                class_result, prob_result = predict(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                }

            else:
                error = "Please upload images of jpg, jpeg, and png extension only"

            if(len(error) == 0):
                return  render_template('success.html', img=img, predictions=predictions)
            else:
                return render_template('index.html', error=error)

    else:
        return render_template('index.html')

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)