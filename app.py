# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re
import os
from flask import Flask, render_template, request,send_file,Response
import cv2
import numpy as np
from io import BytesIO
import base64
import zipfile
input_image_names = []
processed_images = []
errors = []      

app = Flask(__name__,static_folder="static", static_url_path="/static")
app.secret_key = 'your_secret_key'

# SQLite database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if user exists and password is correct
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('upload_files'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/processimage', methods=['GET', 'POST'])
def upload_files():
    result = [] 
    uploads= []
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        conn.close()

        if request.method == 'POST':
            uploaded_files = request.files.getlist('file')
            selected_size = request.form['size']
            standard_size = request.form.get('standard_size')

            if selected_size == 'standard':
                if standard_size == 'small':
                    desired_width = 51
                    desired_height = 51
                elif standard_size == 'medium':
                    desired_width = 35
                    desired_height = 35
                elif standard_size == 'large':
                    desired_width = 45
                    desired_height = 5
            elif selected_size == 'custom':
                desired_width = float(request.form['custom_width'])
                desired_height = float(request.form['custom_height'])
                selected_unit = request.form['selected_unit']
                if selected_unit == 'cm':
                    desired_width *= 10
                    desired_height *= 10
                elif selected_unit == 'inches':
                    desired_width *= 25.4
                    desired_height *= 25.4

            estimated_dpi = 300
            pixels_per_mm_width = estimated_dpi / 25.4
            pixels_per_mm_height = estimated_dpi / 25.4

            for file in uploaded_files:
                if file.filename == '':
                    continue

                image = np.frombuffer(file.read(), np.uint8)
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                height, width = image.shape[:2]
                aspect_ratio = width / height
                if aspect_ratio > 1.0:  # Horizontal image
                    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                    if len(faces)==0:
                        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                    
                    
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                if len(faces) == 0:
                    errors.append(f"No faces detected in {file.filename}.")
                else:
                    retval, buffer1 = cv2.imencode('.jpg', image)
                    image_base = base64.b64encode(buffer1).decode()
                    
                    uploads.append(f"data:image/jpeg;base64,{image_base}")
                    input_image_names.append(file.filename)
                    (x, y, w, h) = faces[0]
                    top_of_head = int(y - 0.42 * h)
                    new_y = max(0, top_of_head)
                    new_h = h + (y - new_y)
                    roi_x = max(0, x - int(0.2 * w))
                    roi_y = new_y
                    roi_w = min(image.shape[1] - roi_x, int(1.4 * w))
                    roi_h = min(image.shape[0] - roi_y, int(1.4 * new_h))
                    cropped_image = image[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
                    center = (int(x - roi_x + roi_w // 2), int(y - roi_y + roi_h // 2))
                    if w > h:
                        angle = -90
                    else:
                        angle = 0

                    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                    aligned_image = cv2.warpAffine(cropped_image, rotation_matrix, (roi_w, roi_h))
                    desired_width_pixels = int(desired_width * pixels_per_mm_width)
                    desired_height_pixels = int(desired_height * pixels_per_mm_height)
                    resized_image = cv2.resize(aligned_image, (desired_width_pixels, desired_height_pixels))
                    processed_images.append(resized_image)
                    retval, buffer = cv2.imencode('.jpg', resized_image)
                    image_base64 = base64.b64encode(buffer).decode()
                    result.append({
                'name': file.filename,
                'image': f"data:image/jpeg;base64,{image_base64}"
            })
        

        return render_template('usp.html', user=user,result=result, errors=errors, original_images=uploads)
    return redirect(url_for('login'))
@app.route('/download_all')
def download_all_images():
        if not processed_images:
            return "No processed images to download."

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for idx, (img, img_name) in enumerate(zip(processed_images, input_image_names)):
                img_path = f"{img_name}"  # Use the input image name as the output image path
                cv2.imwrite(img_path, img)
                zipf.write(img_path)
                os.remove(img_path)  # Remove the temporarily saved image
            
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name="processedimages.zip")
@app.route('/download_errors')
def download_errors():
    error_messages = "\n".join(errors)
    # Create a text file containing the error messages
    response = Response(error_messages, content_type='text/plain')
    response.headers["Content-Disposition"] = "attachment; filename=error_messages.txt"
    return response

# @app.route('/profile')
# def profile():
#     if 'user_id' in session:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
#         user = cursor.fetchone()
#         conn.close()
        
#         if user:
#             return render_template('profile.html', user=user)
    
#     return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
