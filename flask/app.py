import os
import urllib.request
import random
import string
from datetime import datetime
from flask_cors import CORS
from flask import Flask, flash, request, redirect, render_template, abort, jsonify, send_from_directory, send_file, safe_join, abort
from werkzeug.utils import secure_filename
from db_connection import User, UserRegister

app = Flask(__name__, static_folder='static/', template_folder="templates")
CORS(app)
static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client")


UPLOAD_FOLDER = '/app/uploads'
app.secret_key = os.urandom(24)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'mpeg', 'mp4'])



def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def upload_form():
	return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		folder_time = str(datetime.now().timestamp()).replace(".","")
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(UPLOAD_FOLDER, folder_time+"_"+filename))
			flash('File successfully uploaded')
			return jsonify(folder_time+"_"+filename)
		else:
			flash('Allowed file types are png, jpg, jpeg, gif, mpeg, mp4')
			return redirect(request.url)


if __name__ == "__main__":
	UserRegister.post(filename='license_data.csv')
	app.run(host='0.0.0.0', port=5000, debug=True)
	# UserRegister.post(filename='license_data.csv')