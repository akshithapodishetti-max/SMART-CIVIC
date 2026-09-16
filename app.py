from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from PIL import Image
import faiss
import numpy as np
import pickle
import os
from werkzeug.utils import secure_filename
import threading
import webbrowser

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

text_model = SentenceTransformer("all-MiniLM-L6-v2")

vision_model = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32"
)

index = faiss.read_index("index.faiss")

with open("documents.pkl", "rb") as f:
    documents = pickle.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/classify", methods=["POST"])
def classify():

    issue = request.form.get("issue", "")
    detected_issue = "General Issue"
    image_path = ""

    if "photo" in request.files:
        photo = request.files["photo"]

        if photo.filename != "":
            filename = secure_filename(photo.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            photo.save(filepath)

            image_path = "/static/uploads/" + filename

            image = Image.open(filepath).convert("RGB")

            labels = [
                "pothole",
                "garbage",
                "street light",
                "water leak",
                "damaged road"
            ]

            prediction = vision_model(image, candidate_labels=labels)
            detected_issue = prediction[0]["label"]

            print("Prediction:", prediction)
            print("Detected Issue:", detected_issue)

    search_text = issue if issue else detected_issue

    embedding = text_model.encode([search_text])

    _, I = index.search(np.array(embedding), 1)

    result = documents[I[0][0]]
    lines = result.split("\n")

    return jsonify({
        "detected_issue": detected_issue,
        "category": lines[0],
        "department": lines[1].replace("Department: ", ""),
        "priority": lines[2].replace("Priority: ", ""),
        "action": lines[3].replace("Action: ", ""),
        "image": image_path
    })

if __name__ == "__main__":
    threading.Timer(
        1,
        lambda: webbrowser.open("http://127.0.0.1:5000")
    ).start()

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
