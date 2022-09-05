from flask import Flask, render_template, url_for, request
from werkzeug.utils import secure_filename
import os
import torch
import cv2

import requests
requests.packages.urllib3.disable_warnings()

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

UPLOAD_FOLDER = 'static/user_images'

app = Flask(__name__)

model = torch.hub.load("ultralytics/yolov5", "custom", path = 'best3.pt', force_reload=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/demo', methods = ['POST'])
def upload_file():
    if request.method == 'POST':  
        f = request.files['file']
        if f:
            base = (os.path.splitext(f.filename)[0]).replace(" ", "")
            f.filename = base + ".jpg"
            f.save(secure_filename(f.filename))
            results=model(f.filename)
            results.save(save_dir='static/user_images')
            #a=results.split(',')
            #print(results.type())
            #print(results.show())
            confidences = list(results.pandas().xyxy[0]['confidence'])
            format_confidences = []
            for percent in confidences:
                format_confidences.append(str(round(percent*100)) + '%')
            labels = list(results.pandas().xyxy[0]['name'])
            if confidences==[]:
                return render_template('demo.html', user_image=f.filename, confidences="NO DETECTION")
            else:
                return render_template('demo.html', user_image=f.filename, labels=labels[0], confidences=format_confidences[0])        

    return render_template('demo.html', user_image = f.filename)

if __name__ == "__main__":
    app.run(debug=True)
