import os
import cv2
import numpy as np
import sqlite3
import hashlib
import random
from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask import send_from_directory


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///images.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
CORS(app)

# ---------------- DATABASE ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect('project.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# Initialize database
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS tone(colour TEXT PRIMARY KEY, number INT)")
    cursor.execute("INSERT OR IGNORE INTO tone VALUES ('cool', 0)")
    cursor.execute("INSERT OR IGNORE INTO tone VALUES ('warm', 0)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dress(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dtype TEXT,
        colour TEXT,
        undertones TEXT,
        weather TEXT,
        occasion1 TEXT,
        imagepath TEXT,
        wearcount INT DEFAULT 0
    )
    """)
    # Add wearcount column if missing
    try:
        cursor.execute("ALTER TABLE dress ADD COLUMN wearcount INT DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()


# ---------------- IMPROVED COLOR DETECTION ----------------
def detectcolor(imagepath):
    img = cv2.imread(imagepath)
    if img is None:
        return "unknown"

    img = cv2.resize(img, (200, 200))

    # Convert to grayscale for black/white detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 5)

    # Black detection
    if np.mean(blurred) < 50:
        return "black"

    # White detection
    _, thresh = cv2.threshold(blurred, 240, 255, cv2.THRESH_BINARY)
    white_ratio = cv2.countNonZero(thresh) / thresh.size
    if white_ratio > 0.85:
        return "white"

    # HSV color detection with improved ranges
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    ranges = {
        "yellow": ([25, 50, 50], [35, 255, 255]),
        "orange": ([11, 50, 50], [25, 255, 255]),
        "red": ([0, 50, 50], [15, 255, 255]),
        "green": ([40, 50, 50], [85, 255, 255]),
        "blue": ([100, 50, 50], [140, 255, 255]),
        "purple": ([140, 50, 50], [160, 255, 255])
    }

    for color, (lower, upper) in ranges.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        color_ratio = np.count_nonzero(mask) / mask.size
        if color_ratio > 0.1:
            return color

    return "None"


# ---------------- UNDERTONE ----------------
@app.route("/undertone", methods=["POST"])
def undertone():
    data = request.get_json()
    if not data or "answer" not in data:
        return jsonify({"error": "Missing answer field"}), 400

    temp = data["answer"]

    cool = ['hazeleye', 'ambereye', 'browneye', 'blackeye', 'greenvein', 'suntan', 'whiteyellow',
            'caramelhair', 'richbrownhair', 'redhair', 'yellowhair', 'goldjewellery']
    warm = ['grayeye', 'greeneye', 'blueeye', 'bluevein', 'notan', 'whitepink', 'whiteblue',
            'whitered', 'blackhair', 'grayhair', 'ashybrownhair', 'silverjewellery']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        if temp in cool:
            cursor.execute("UPDATE tone SET number=number+1 WHERE colour='cool'")
        elif temp in warm:
            cursor.execute("UPDATE tone SET number=number+1 WHERE colour='warm'")
        conn.commit()

    return jsonify({"status": "recorded"})


@app.route("/finaltone", methods=["GET"])
def finaltone():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT number FROM tone WHERE colour='cool'")
        cool_result = cursor.fetchone()
        cool1 = cool_result[0] if cool_result else 0

        cursor.execute("SELECT number FROM tone WHERE colour='warm'")
        warm_result = cursor.fetchone()
        warm1 = warm_result[0] if warm_result else 0

    if cool1 > warm1:
        sk = "Cool"
    elif warm1 > cool1:
        sk = "Warm"
    else:
        sk = "Neutral"

    return jsonify({"undertone": sk})


# ---------------- IMAGE UPLOAD ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), unique=True, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    detected_color = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

def get_file_hash(file):
    hasher = hashlib.sha256()
    file.seek(0)
    hasher.update(file.read())
    file.seek(0)
    return hasher.hexdigest()

@app.route("/wardrobe/uploadAndDetect", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    file_hash = get_file_hash(file)
    existing_image = Image.query.filter_by(file_hash=file_hash).first()
    if existing_image:
        return jsonify({"message": "File already exists"}), 409
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    detected_color = detectcolor(path)
    new_image = Image(
        filename=filename,
        file_hash=file_hash,
        file_path=path,
        detected_color=detected_color
    )

    db.session.add(new_image)
    db.session.commit()
    
    image_url = request.host_url + "uploads/" + filename

    return jsonify({
        "message": "File uploaded successfully",
        "image_url": image_url,
        "detected_color": detected_color
    })



# ---------------- ADD DRESS ----------------
@app.route("/add_dress", methods=["POST"])
def add_dress():
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400

    file = request.files["image"]
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    data = request.form
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    colour = detectcolor(path)
    dtype = data.get("dtype", "")
    undertone = data.get("undertone", "Neutral")
    weather = data.get("weather", "")
    occasion1 = data.get("occasion", "")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dress(dtype, colour, undertones, weather, occasion1, imagepath, wearcount)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (dtype, colour, undertone, weather, occasion1, path))
        conn.commit()

    return jsonify({"message": "Dress added successfully"})

#_______________DELETE DRESS__________________#


@app.route("/delete_dress/<int:dress_id>", methods=["DELETE"])
def delete_dress(dress_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 1. Get the image path first so we can delete the file
            cursor.execute("SELECT imagepath FROM dress WHERE id=?", (dress_id,))
            row = cursor.fetchone()

            if row:
                image_path = row['imagepath']
                
                # Delete the file from the 'uploads' folder if it exists
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)

                # 2. Delete the record from the database
                cursor.execute("DELETE FROM dress WHERE id=?", (dress_id,))
                conn.commit()
                return jsonify({"message": "Dress deleted successfully"}), 200
            else:
                return jsonify({"error": "Dress not found"}), 404
    except Exception as e:
        # Catch unexpected errors
        return jsonify({"error": str(e)}), 500



# ---------------- SCORING SYSTEM ----------------
occasionpriority = {
    "Festive": ["Ethnic Wear", "Kurta", "Palazzo", "Dress"],
    "Casual": ["Jeans", "Tshirt", "Shorts", "Skirt"],
    "Formal": ["Blazer", "Coat", "Formal Trousers"],
    "Party": ["Dress", "Skirt", "Blouse"],
    "Sports": ["Tracksuit", "Shorts"]
}

weatherpriority = {
    "Summer": ["Dress", "Skirt", "Shorts", "Blouse"],
    "Winter": ["Coat", "Jacket", "Sweater", "Cardigan"],
    "Monsoon": ["Jeans", "Kurta", "Palazzo"]
}

undertonepriority = {
    "Warm": ["yellow", "orange", "red"],
    "Cool": ["blue", "green", "black"],
    "Neutral": ["white", "black", "blue", "gray"]
}

COLOR_COMPATIBILITY = {
    "black": ["white", "blue", "red", "green", "yellow"],
    "white": ["black", "blue", "red", "green"],
    "blue": ["white", "black", "gray"],
    "red": ["black", "white", "blue"],
    "green": ["white", "black"],
    "yellow": ["black", "blue", "white"],
    "orange": ["white", "black", "blue"],
    "gray": ["black", "white", "blue"],
    "purple": ["white", "black", "gray"]
}

BOTTOM_MATCHING = {
    "Kurta": ["Palazzo", "Jeans", "Churidar"],
    "Tshirt": ["Jeans", "Shorts"],
    "Blouse": ["Skirt", "Palazzo"],
    "Blazer": ["Formal Trousers"],
    "Coat": ["Formal Trousers"],
    "Sweater": ["Jeans"],
    "Jacket": ["Jeans"],
    "Dress": ["None"]
}


def wear_penalty(wearcount):
    return wearcount * 10

def calculate_score(row, occ, wea, skin, use_weather, use_skin):
    score = 15

    if row['dtype'] in occasionpriority.get(occ, []):
        score += 30

    if use_weather and row['dtype'] in weatherpriority.get(wea, []):
        score += 20

    if use_skin and row['colour'] in undertonepriority.get(skin, []):
        score += 10

    score -= wear_penalty(row['wearcount'])
    return score


def choose_bottom(top_type, top_color, occ, wea):
    options = BOTTOM_MATCHING.get(top_type, [])
    if not options or "None" in options:
        return None

    with get_db_connection() as conn:
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in options)
        cursor.execute(f"SELECT * FROM dress WHERE dtype IN ({placeholders})", options)
        bottoms = cursor.fetchall()

    scored = []
    for b in bottoms:
        s = 0
        if b['occasion1'] == occ:
            s += 30
        if b['weather'] == wea:
            s += 20
        if b['colour'] in COLOR_COMPATIBILITY.get(top_color, []):
            s += 25
        s -= b['wearcount'] * 5
        scored.append((s, b))

    if not scored:
        return None
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0]


# ---------------- RECOMMEND ----------------
@app.route("/api/top-picks", methods=["POST"])
def recommend():
    data = request.get_json()
    if not all(key in data for key in ["occasion", "weather", "undertone"]):
        return jsonify({"error": "Missing required fields"}), 400

    occ = data["occasion"]
    wea = data["weather"]
    skin = data["undertone"]

    use_weather = data.get("use_weather", True)
    use_skin = data.get("use_undertone", True)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dress")
        rows = cursor.fetchall()

    scored = [(calculate_score(r, occ, wea, skin, use_weather, use_skin), r) for r in rows]
    scored.sort(key=lambda x: x[0], reverse=True)

    result = []
    for s, r in scored[:1]:
        bottom = choose_bottom(r['dtype'], r['colour'], occ, wea)

        result.append({
            "topwear": r['dtype'],
            "bottomwear": bottom[1]['dtype'] if bottom else "None",
            "bottom_color": bottom[1]['colour'] if bottom else "None",
            "top_image": request.host_url + r['imagepath'],
            "score":f" {s*100//55}% match"
        })

    return jsonify(result)


# ---------------- WEAR UPDATE ----------------
@app.route("/wear", methods=["POST"])
def wear():
    data = request.get_json()
    if "id" not in data:
        return jsonify({"error": "Missing id field"}), 400

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE dress SET wearcount=wearcount+1 WHERE id=?", (data["id"],))
        if cursor.rowcount == 0:
            return jsonify({"error": "Dress not found"}), 404
        conn.commit()

    return jsonify({"message": "Wear updated"})


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)