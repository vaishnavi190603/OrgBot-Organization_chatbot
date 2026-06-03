from flask import Flask, request, jsonify, render_template, session, redirect
from Bot_Final import UltraChatBot
import json
import firebase_admin
from firebase_admin import credentials, db
import os
import pdfplumber
import re
import nltk
from transformers import T5Tokenizer, T5ForConditionalGeneration
from pdf_chatbot import extract_text_from_pdf, generate_answer

# Ensure NLTK tokenizer is available
nltk.download("punkt", quiet=True)
from nltk.tokenize import sent_tokenize

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize Firebase Admin SDK
cred = credentials.Certificate("fbconfig.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://projectcg4-6c3b1-default-rtdb.firebaseio.com/'
})

PROJECT_UPLOAD_FOLDER = "uploads"  # Inside the project directory
EXTERNAL_UPLOAD_FOLDER = "C:/Saved_PDFs"  # Specific location in D drive

# Ensure both folders exist
os.makedirs(PROJECT_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTERNAL_UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    for user_type in ['users', 'employees']:
        users_ref = db.reference(user_type)
        users_data = users_ref.get()
        if users_data:
            for user_id, user_info in users_data.items():
                if user_info.get("email") == email and user_info.get("password") == password:
                    session['user'] = user_id
                    session['user_type'] = user_type
                    return jsonify({"success": True, "redirect": "/bot"}), 200
    return jsonify({"success": False, "message": "Invalid credentials."}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name, email, contact, password, confirm_password, user_type = data.values()
    
    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match!"}), 400

    node = "users" if user_type == "user" else "employees"
    users_ref = db.reference(node)

    # ✅ Replace spaces with underscores to create a Firebase-safe key
    safe_name = name.replace(" ", "_")

    existing_users = users_ref.get() or {}
    if safe_name in existing_users:
        return jsonify({"success": False, "message": "Username already taken!"}), 409

    users_ref.child(safe_name).set({
        'email': email, 
        'contact': contact, 
        'password': password, 
        'user_type': user_type 
    })

    # ✅ Store the safe_name in session for future use
    session["user_name"] = safe_name  
    session["user_type"] = node  

    return jsonify({"success": True, "redirect": "/"}), 201


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/bot')
def index():
    if 'user' not in session:
        return redirect('/')
    return render_template('index.html')

@app.route('/mybot', methods=['POST'])
def mybot():
    user_type = session.get('user_type', 'user')
    user_message = request.json.get('data', '')
    bot = UltraChatBot(user_type)
    bot_response = bot.process_incoming_message(user_message)
    return jsonify(bot_response)

@app.route("/pdf.html")
def upload_pdf_page():
    return render_template("pdf.html")

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    if "user_name" not in session:
        return jsonify({"success": False, "message": "User not logged in."}), 401

    user_name = session["user_name"]  # Now contains a Firebase-safe format
    user_type = session["user_type"]

    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded."}), 400

    file = request.files["file"]
    
    if file.filename == "" or not file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "message": "Invalid file format."}), 400

    # Define file paths
    project_path = os.path.join("uploads", file.filename)
    external_path = os.path.join("C:/Saved_PDFs", file.filename)

    try:
        # Save the file in both locations
        file.save(project_path)
        file.save(external_path)

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(project_path)
        session["pdf_text"] = extracted_text

        # ✅ Store file info under the user's safe name
        user_ref = db.reference(f"{user_type}/{user_name}/uploaded_files")
        file_entry = {
            "project_path": project_path,
            "external_path": external_path
        }
        user_ref.child(file.filename.replace(".", "_")).set(file_entry)  # Replace "." to avoid Firebase errors

        return jsonify({
            "success": True,
            "message": "PDF uploaded successfully!",
            "project_path": project_path,
            "external_path": external_path
        })
    except Exception as e:
        print(f"Error saving file to Firebase: {e}")
        return jsonify({"success": False, "message": f"Error saving file: {str(e)}"}), 500



@app.route("/ask", methods=["POST"])
def ask_question():
    question = request.json.get("question", "")
    context = session.get('pdf_text', "")
    answer = generate_answer(question, context)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
